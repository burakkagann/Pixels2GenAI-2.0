# Pixels2GenAI

**Write the code behind generative art.**

Free Python lessons, from a single pixel to generative AI. You write the rule, then the data does, then the model. The curriculum was built and tested in a master's thesis and is taught in workshops in Berlin.

**[Open the lessons at pixels2genai.art](https://pixels2genai.art)**. Lessons in Modules 1 to 8 run their Python in your browser, with nothing to install and no account.

## The project

| Part | What it is |
|---|---|
| **[Lessons](https://pixels2genai.art/#curriculum)** | 15 modules and a capstone in three paths. 192 lessons planned, 71 live (7 November 2026). Each lesson has three exercises: run, modify, create. |
| **[Research](https://pixels2genai.art/research)** | A master's thesis using design-based research. In a one-day pilot in Berlin on 12 February 2026, the mean score of the eight participants who took both tests rose from 3.6 to 12.1 out of 24. |
| **[Workshops](https://pixels2genai.art/workshops)** | Six Saturdays in Berlin from 5 December 2026, hosted by Kristian Rother at Academis. |
| **[Exhibition](https://pixels2genai.art/exhibitions/2026-03)** | Prints made with code, shown at IT studio Academis in Berlin on 27 and 28 March 2026. |
| **Open** | Code under MIT, our own lesson text and figures under CC BY 4.0, [third-party items excepted](LICENSE-CONTENT.md#third-party-material). **Teachers can use, adapt and translate them**, with credit as in [LICENSE-CONTENT.md](LICENSE-CONTENT.md). |

## What you make

Three module cards per path, the first modules with live lessons. Each card opens its first lesson; a planned module opens the curriculum.

### I · Foundations

You write the rule, with NumPy and PIL. Modules 0 to 5.

<a href="https://pixels2genai.art/lessons/1.1.1"><img src=".github/readme/m01-light.webp#gh-light-mode-only" width="208" alt="M 01 Pixel Fundamentals: 9 lessons, 5 live"></a><a href="https://pixels2genai.art/lessons/1.1.1"><img src=".github/readme/m01-dark.webp#gh-dark-mode-only" width="208" alt="M 01 Pixel Fundamentals: 9 lessons, 5 live"></a>
<a href="https://pixels2genai.art/lessons/2.1.1"><img src=".github/readme/m02-light.webp#gh-light-mode-only" width="208" alt="M 02 Geometry & Mathematics: 13 lessons, 10 live"></a><a href="https://pixels2genai.art/lessons/2.1.1"><img src=".github/readme/m02-dark.webp#gh-dark-mode-only" width="208" alt="M 02 Geometry & Mathematics: 13 lessons, 10 live"></a>
<a href="https://pixels2genai.art/lessons/3.1.1"><img src=".github/readme/m03-light.webp#gh-light-mode-only" width="208" alt="M 03 Transformations & Effects: 17 lessons, 15 live"></a><a href="https://pixels2genai.art/lessons/3.1.1"><img src=".github/readme/m03-dark.webp#gh-dark-mode-only" width="208" alt="M 03 Transformations & Effects: 17 lessons, 15 live"></a>

### II · Machine Learning

The data writes the rule, with NumPy, PyTorch and TouchDesigner. Modules 6 to 11.

<a href="https://pixels2genai.art/lessons/6.1.1"><img src=".github/readme/m06-light.webp#gh-light-mode-only" width="208" alt="M 06 Noise & Procedural Generation: 15 lessons, 1 live"></a><a href="https://pixels2genai.art/lessons/6.1.1"><img src=".github/readme/m06-dark.webp#gh-dark-mode-only" width="208" alt="M 06 Noise & Procedural Generation: 15 lessons, 1 live"></a>
<a href="https://pixels2genai.art/lessons/8.1.1"><img src=".github/readme/m08-light.webp#gh-light-mode-only" width="208" alt="M 08 Animation & Time: 14 lessons, 5 live"></a><a href="https://pixels2genai.art/lessons/8.1.1"><img src=".github/readme/m08-dark.webp#gh-dark-mode-only" width="208" alt="M 08 Animation & Time: 14 lessons, 5 live"></a>
<a href="https://pixels2genai.art/lessons/9.1.1"><img src=".github/readme/m09-light.webp#gh-light-mode-only" width="208" alt="M 09 Neural Networks: 12 lessons, 6 live"></a><a href="https://pixels2genai.art/lessons/9.1.1"><img src=".github/readme/m09-dark.webp#gh-dark-mode-only" width="208" alt="M 09 Neural Networks: 12 lessons, 6 live"></a>

### III · Generative AI

The model makes the image, with PyTorch. Modules 12 to 15. Lessons include the outputs of their GPU runs.

<a href="https://pixels2genai.art/lessons/12.1.1"><img src=".github/readme/m12-light.webp#gh-light-mode-only" width="208" alt="M 12 Generative AI Models: 15 lessons, 15 live"></a><a href="https://pixels2genai.art/lessons/12.1.1"><img src=".github/readme/m12-dark.webp#gh-dark-mode-only" width="208" alt="M 12 Generative AI Models: 15 lessons, 15 live"></a>
<a href="https://pixels2genai.art/#curriculum"><img src=".github/readme/m13-light.webp#gh-light-mode-only" width="205" alt="M 13 AI + TouchDesigner: 12 lessons, planned"></a><a href="https://pixels2genai.art/#curriculum"><img src=".github/readme/m13-dark.webp#gh-dark-mode-only" width="205" alt="M 13 AI + TouchDesigner: 12 lessons, planned"></a>
<a href="https://pixels2genai.art/#curriculum"><img src=".github/readme/m14-light.webp#gh-light-mode-only" width="205" alt="M 14 Data as Material: 14 lessons, planned"></a><a href="https://pixels2genai.art/#curriculum"><img src=".github/readme/m14-dark.webp#gh-dark-mode-only" width="205" alt="M 14 Data as Material: 14 lessons, planned"></a>

## How a lesson works

Each lesson has three exercises:

1. **Execute**: run a complete script and look at the result.
2. **Modify**: change two to five labelled parameters and compare the output.
3. **Create**: finish a starter script, with hints and a full solution.

Lessons in Modules 0 to 6 take 15 to 20 minutes. Lessons in Modules 7 to 15 take 30 to 45.

## Run the site locally

Only needed to work on the site. It is an [Astro](https://astro.build) site and needs Node 20.

```bash
git clone https://github.com/burakkagann/Pixels2GenAI-2.0.git
cd Pixels2GenAI-2.0
npm install
npm run dev        # http://localhost:4321
npm run status     # live lessons per module
```

## Contributing

The most useful contribution is porting a lesson that is not live yet from the [first edition](https://burakkagann.github.io/Pixels2GenAI/). Workflow and checklist: [CONTRIBUTING.md](CONTRIBUTING.md). For a bug or a lesson that stops making sense, [open an issue](https://github.com/burakkagann/Pixels2GenAI-2.0/issues).

## License and citation

Code: [MIT](LICENSE). Our own lesson text and figures: [CC BY 4.0](LICENSE-CONTENT.md), [third-party items excepted](LICENSE-CONTENT.md#third-party-material). To cite the curriculum, use [CITATION.cff](CITATION.cff) or the "Cite this repository" button.

The M 12 card shows building facades generated by a model trained on the CMP Facade Database (Tyleček & Šára, 2013).

© 2026 Burak Kağan Yılmazer and Kristian Rother.
