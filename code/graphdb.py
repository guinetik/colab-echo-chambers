from dotenv import load_dotenv
import os
import base64
import io
import json
import pandas as pd
from flask import Flask, request, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

class GraphDataSource:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def create_user_node(self, user_id, name, gender, birth_date, city_id, city_name, state_id, state_name, created_at, last_sign_in_at, device, lat, lng):
        with self.driver.session() as session:
            session.run("CREATE (:User {user_id: $user_id, name: $name, gender: $gender, birth_date: $birth_date, city_id: $city_id, "
                        "city_name: $city_name, state_id: $state_id, state_name: $state_name, created_at: $created_at, "
                        "last_sign_in_at: $last_sign_in_at, device: $device, lat: $lat, lng: $lng})",
                        user_id=user_id, name=name, gender=gender, birth_date=birth_date, city_id=city_id, city_name=city_name,
                        state_id=state_id, state_name=state_name, created_at=created_at, last_sign_in_at=last_sign_in_at,
                        device=device, lat=lat, lng=lng)
    
    def create_follows_relationship(self, source_user_id, target_user_id, model_key, created_at):
        model_id = self.get_model_id(model_key)
        if model_id is None:
            return None
        with self.driver.session() as session:
            session.run("MATCH (source:User {user_id: $source_user_id}) "
                        "MATCH (target:User {user_id: $target_user_id}) "
                        "MATCH (model:Model {model_id: $model_id}) "
                        "CREATE (source)-[:FOLLOWS {created_at: $created_at}]->(target)-[:PART_OF]->(model)",
                        source_user_id=source_user_id, target_user_id=target_user_id, model_id=model_id, created_at=created_at)
    
    def get_followers(self, user_id, model_key):
        model_id = self.get_model_id(model_key)
        if model_id is None:
            return None
        with self.driver.session() as session:
            result = session.run("MATCH (source:User)-[:FOLLOWS]->(target:User {user_id: $user_id})-[:PART_OF]->(model:Model {model_id: $model_id}) "
                                 "RETURN source.user_id, source.name",
                                 user_id=user_id, model_id=model_id)
            return [(record['source.user_id'], record['source.name']) for record in result]
    
    def get_following(self, user_id, model_key):
        model_id = self.get_model_id(model_key)
        if model_id is None:
            return None
        with self.driver.session() as session:
            result = session.run("MATCH (source:User {user_id: $user_id})-[:FOLLOWS]->(target:User)-[:PART_OF]->(model:Model {model_id: $model_id}) "
                                 "RETURN target.user_id, target.name",
                                 user_id=user_id, model_id=model_id)
            return [(record['target.user_id'], record['target.name']) for record in result]
    
    def get_user(self, user_id):
        with self.driver.session() as session:
            result = session.run("MATCH (user:User {user_id: $user_id}) "
                                 "RETURN user.user_id, user.name, user.gender, user.birth_date, user.city_id, "
                                 "user.city_name, user.state_id, user.state_name, user.created_at, "
                                 "user.last_sign_in_at, user.device, user.lat, user.lng",
                                 user_id=user_id)
            record = result.single()
            
            if record is not None:
                user = {
                    'user_id': record['user.user_id'],
                    'name': record['user.name'],
                    'gender': record['user.gender'],
                    'birth_date': record['user.birth_date'],
                    'city_id': record['user.city_id'],
                    'city_name': record['user.city_name'],
                    'state_id': record['user.state_id'],
                    'state_name': record['user.state_name'],
                    'created_at': record['user.created_at'],
                    'last_sign_in_at': record['user.last_sign_in_at'],
                    'device': record['user.device'],
                    'lat': record['user.lat'],
                    'lng': record['user.lng']
                }
                
                return user
            else:
                return None
    
    def follow(self, source_user_id, target_user_id, model_key, created_at):
        model_id = self.get_model_id(model_key)
        if model_id is None:
            return False
        self.create_follows_relationship(source_user_id, target_user_id, model_id, created_at)
        return True
    
    def unfollow(self, source_user_id, target_user_id, model_key):
        model_id = self.get_model_id(model_key)
        if model_id is None:
            return False
        with self.driver.session() as session:
            session.run("MATCH (source:User {user_id: $source_user_id})-[r:FOLLOWS]->(target:User {user_id: $target_user_id})-[:PART_OF]->(model:Model {model_id: $model_id}) "
                        "DELETE r",
                        source_user_id=source_user_id, target_user_id=target_user_id, model_id=model_id)
        return True


class Neo4jBatchImporter:
    def __init__(self, graph_data_source):
        self.graph_data_source = graph_data_source
    
    def import_data(self, model_key, nodes_csv=None, edges_csv=None, nodes_json=None, edges_json=None):
        if nodes_csv:
            self._import_nodes_from_csv(nodes_csv)
        
        if edges_csv:
            self._import_edges_from_csv(edges_csv, model_key)
        
        if nodes_json:
            self._import_nodes_from_json(nodes_json)
        
        if edges_json:
            self._import_edges_from_json(edges_json, model_key)
    
    def _import_edges_from_dataframe(self, edges_df, model_key):
        for _, row in edges_df.iterrows():
            source_user_id = row['source']
            target_user_id = row['target']
            created_at = row['created_at']
            
            self.graph_data_source.create_follows_relationship(source_user_id, target_user_id, model_key, created_at)
    
    def _import_edges_from_json(self, edges_json, model_key):
        edges_data = base64.b64decode(edges_json)
        edges_df = pd.read_csv(io.BytesIO(edges_data))
        self._import_edges_from_dataframe(edges_df, model_key)
    
    def _import_edges_from_json(self, edges_json, model_key):
        edges_data = base64.b64decode(edges_json)
        edges_json_str = edges_data.decode('utf-8')
        edges_list = json.loads(edges_json_str)
        
        edges_df = pd.DataFrame(edges_list)
        
        self._import_edges_from_dataframe(edges_df, model_key)
    
    def _import_nodes_from_csv(self, nodes_csv):
        nodes_data = base64.b64decode(nodes_csv)
        colab_users = pd.read_csv(io.BytesIO(nodes_data))
        
        for _, row in colab_users.iterrows():
            user_id = row['id']
            name = row['name']
            gender = row['gender']
            birth_date = row['birth_date']
            city_id = row['city_id']
            city_name = row['city_name']
            state_id = row['state_id']
            state_name = row['state_name']
            created_at = row['created_at']
            last_sign_in_at = row['last_sign_in_at']
            device = row['device']
            lat = row['lat']
            lng = row['lng']
            self.graph_data_source.create_user_node(user_id, name, gender, birth_date, city_id,
                            city_name, state_id, state_name, created_at, last_sign_in_at, device, lat, lng)
    
    def _import_nodes_from_json(self, nodes_json):
        nodes_data = base64.b64decode(nodes_json)
        nodes_csv = pd.read_csv(io.BytesIO(nodes_data))
        
        self._import_nodes_from_csv(nodes_csv)

class App:
    def __init__(self):
        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        self.graph_data_source = GraphDataSource(uri, username, password)
        self.neo4j_importer = Neo4jBatchImporter(self.graph_data_source)
        
        self.app = Flask(__name__)
        
        self.app.route('/create_user', methods=['POST'])(self.create_user)
        self.app.route('/follow', methods=['POST'])(self.follow)
        self.app.route('/unfollow', methods=['POST'])(self.unfollow)
        self.app.route('/followers', methods=['GET'])(self.get_followers)
        self.app.route('/following', methods=['GET'])(self.get_following)
        self.app.route('/user', methods=['GET'])(self.get_user)
        self.app.route('/import_csv', methods=['POST'])(self.import_csv)
        
    def create_user(self):
        data = request.json
        
        user_id = data['user_id']
        name = data['name']
        gender = data['gender']
        birth_date = data['birth_date']
        city_id = data['city_id']
        city_name = data['city_name']
        state_id = data['state_id']
        state_name = data['state_name']
        created_at = data['created_at']
        last_sign_in_at = data['last_sign_in_at']
        device = data['device']
        lat = data['lat']
        lng = data['lng']
        
        self.graph_data_source.create_user_node(user_id, name, gender, birth_date, city_id, city_name, state_id,
                                                state_name, created_at, last_sign_in_at, device, lat, lng)
        
        return jsonify({'message': 'User created successfully'}), 201
    
    def follow(self):
        data = request.json
        
        source_user_id = data['source_user_id']
        target_user_id = data['target_user_id']
        model_key = data['model_key']
        created_at = data['created_at']
        
        success = self.graph_data_source.follow(source_user_id, target_user_id, model_key, created_at)
        
        if success:
            return jsonify({'message': 'Followed successfully'}), 201
        else:
            return jsonify({'message': 'Failed to follow'}), 400
    
    def unfollow(self):
        data = request.json
        
        source_user_id = data['source_user_id']
        target_user_id = data['target_user_id']
        model_key = data['model_key']
        
        success = self.graph_data_source.unfollow(source_user_id, target_user_id, model_key)
        
        if success:
            return jsonify({'message': 'Unfollowed successfully'}), 200
        else:
            return jsonify({'message': 'Failed to unfollow'}), 400
    
    def import_csv(self):
        data = request.json
        
        model_key = data['model_key']
        nodes_csv = data.get('nodes_csv')
        edges_csv = data.get('edges_csv')
        
        self.neo4j_importer.import_data(model_key, nodes_csv, edges_csv)
        
        return jsonify({'message': 'Data imported successfully'}), 201
    
    def get_followers(self):
        user_id = request.args.get('user_id')
        model_key = request.args.get('model_key')
        
        followers = self.graph_data_source.get_followers(user_id, model_key)
        
        if followers is not None:
            return jsonify({'followers': followers}), 200
        else:
            return jsonify({'message': 'Failed to get followers'}), 400
    
    def get_following(self):
        user_id = request.args.get('user_id')
        model_key = request.args.get('model_key')
        
        following = self.graph_data_source.get_following(user_id, model_key)
        
        if following is not None:
            return jsonify({'following': following}), 200
        else:
            return jsonify({'message': 'Failed to get following'}), 400
    
    def get_user(self):
        user_id = request.args.get('user_id')
        
        user = self.graph_data_source.get_user(user_id)
        
        if user:
            followers = self.graph_data_source.get_followers(user_id)
            following = self.graph_data_source.get_following(user_id)
            
            return jsonify({
                'user': user,
                'followers': followers,
                'following': following
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    
    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = App()
    app.run()