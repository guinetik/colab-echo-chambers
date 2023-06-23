# colab-echo-chambers
This is the repository for the paper on the [Social Network Graph](https://en.wikipedia.org/wiki/Social_network_analysis) and [Echo Chambers](https://en.wikipedia.org/wiki/Echo_chamber_(media)) on the [Colab.re App](https://colab.re). This is my final project for the Masters Degree in Software Engineering for [Cesar School](https://cesar.school). This readme is mostly for the benefit of _future me_ so I'd have a clue on what I was doing when I was working on this. You can use for yourself as a template, but don't trust my code.

## Motivation

Everyone recomended I use [Overleaf](https://pt.overleaf.com/), but since this is my first LaTeX adventure, I feel like I want to learn how this stuff works from the ground up. Also, I`m comfortable writing in the tools I already know like VSCode and IntelliJ. Futhermore, I don't want to vendor-lock-in my paper with a cloud provider when I can just as easily setup cloud storage with github. Anyway, maybe I'll get stuck and move back to Overleaf, maybe I'll learn cool stuff about LaTeX...

## Templating
For templating I started with this [IEEE LaTex Template](https://latextemplates.github.io/IEEE/). But it was an english/german package threw me off hard when I couldn't make it work in pt-br.

So I got this [SBC Template](https://www.sbc.org.br/documentos-da-sbc/summary/169-templates-para-artigos-e-capitulos-de-livros/878-modelosparapublicaodeartigos). It worked first time, so I'm sticking with it for now.

Finally, I settled on using [thesis-model-icmc](https://github.com/lordantonelli/thesis-model-icmc) by [lordantonelli(https://github.com/lordantonelli/)] which is fully compatible with the ABNT2 ruleset. It was recommended by my professor and it has been tailored to Cesar School's template.

I'm versioning these templates for achival purposes. Maybe by the time I revisit these links, they`re gonzo...

## Installing

You need to have a TeX compiler installed. For Windows, I used [MiKTeX](https://miktex.org/download). People recommended [LiveTeX](https://www.tug.org/texlive/windows.html), however the package is [over 4gb which mostly due to coming bundled with source code](https://tex.stackexchange.com/questions/119759/why-cant-tex-lives-size-be-reduced), perl and docs. To me is an overkill, I like that MiKTeX comes with a package manager and install stuff as needed. Currently with all the packages I need for the paper, the MiKTeX folder is less than 1gb in comparison.
``` bash
choco install miktex
```

For main editing, I started with TeXMaker:
``` bash
choco install texmaker
```

Then I quickly discovered the [LaTeXWorkshop](https://github.com/James-Yu/LaTeX-Workshop) for VSCode. For me it's much better, but it requires Perl. So let's install StrawberryPerl for Windows:
``` bash
choco install strawberryperl
```

For managing the references, I use JabRef. The main ref file is `./paper/colab-echo-chambers.bib`. Install JabRef with:
``` bash
choco install jabref
```

## Compiling

From the `./paper` directory, run:
```
pdflatex -halt-on-error -output-directory ../out main.tex
```
The file will be saved in the `./out` directory.

### Docker

Alternatively if you don't want to install any of the above dependencies, you can use Docker. Build the image with: `docker build -t guinetik/ltx .` 

Then run the container pointing to the main.tex file:

```
docker run --rm -it -v $(pwd):/sources guinetik/ltx pdflatex -halt-on-error -output-directory out main.tex
```

### Full Build Script

To accomodate features like nomeclature, bibliography and glossary, I created a multi-stage build script in `paper/build.sh`. To execute this script in Docker, run:

```
docker run --rm -it -v "$(pwd)":/sources guinetik/ltx ./build.sh
```

#### Demo
![Docker Demo](docker.gif "Docker Demo")

## Building in VSCode
Since the ICMC class uses packages that requires multiple LaTeX runs, the default build command in [LaTeXWorkshop](https://github.com/James-Yu/LaTeX-Workshop) won't generate the index based items like nomeclature and glossary. I have created a custom build command in [VSCode's settings.json](.vscode/settings.json) that covers all the build steps.

## Github Actions

I'm using Github Actions to build the paper PDF on every commit. The workflow is defined in [buildpdf.yaml](.github/workflows/buildpdf.yaml). It uses [latex-action](https://github.com/marketplace/actions/latex-compilation) to execute the same build I use locally. The output is saved as an artifact and can be downloaded from the Actions tab. It also creates a release and add the PDF as an asset. This way I can download the PDF from the Releases tab.