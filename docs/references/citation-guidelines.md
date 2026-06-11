# Citation Guidelines (APA 7th Edition)

**Source**: Extracted from CLAUDE.md Citation Guidelines section
**Purpose**: Ensure all modules cite sources for pedagogical claims, algorithmic origins, historical context, technical specifications, and "Did You Know?" facts.

---

## Minimum Citation Requirements

- **Modules 0-6** (Foundation/Hands-On): 5-7 citations minimum
- **Modules 7-15** (Advanced/Theory): 7-10 citations minimum

**Quality over quantity**: Cite credible academic sources, official documentation, and respected textbooks. Avoid blog posts unless from recognized experts.

---

## In-Text Citation Formats

**Single author**: `(Smith, 2020)` or `Smith (2020) demonstrates that...`

**Two authors**: `(Smith & Jones, 2020)`

**Three or more**: `(Smith et al., 2020)`

**Direct quote**: `(Smith, 2020, p. 42)`

**Multiple citations**: `(Galanter, 2016; McCormack & d'Inverno, 2012; Pearson, 2011)`

---

## Reference List Formats

### Journal Articles
> Galanter, P. (2016). Generative art theory. In C. Paul (Ed.), *A Companion to Digital Art* (pp. 146-180). Wiley-Blackwell. https://doi.org/10.1002/9781118475249.ch8

### Books
> Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. ISBN: 978-0-262-03561-3

### Book Chapters
> Reas, C., & Fry, B. (2010). Getting started with Processing. In M. Pearson (Ed.), *Generative Art* (pp. 34-56). Manning Publications.

### Websites (Official Documentation)
> NumPy Developers. (2024). NumPy array creation routines. *NumPy Documentation*. Retrieved January 15, 2025, from https://numpy.org/doc/stable/reference/routines.array-creation.html

### arXiv Preprints
> Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). High-resolution image synthesis with latent diffusion models. *arXiv preprint*. https://arxiv.org/abs/2112.10752

### Software/Code Libraries
> Clark, A., et al. (2024). *Pillow: Python Imaging Library* (Version 10.2.0) [Computer software]. Python Software Foundation. https://python-pillow.org/

---

## RST Implementation (v1 source format)

**In-text**:
```rst
Generative art uses autonomous systems to create artwork [Galanter2016]_. Early pioneers like Harold Cohen developed AARON [McCormack2014]_.
```

**References section** (at end of file):
```rst
References
==========

.. [Galanter2016] Galanter, P. (2016). Generative art theory...
.. [McCormack2014] McCormack, J., et al. (2014). Ten questions...
```

## MDX Implementation (v2 published format)

The v2 lesson MDX files render references as a numbered list at the bottom, inside `<section class="refs">`. Tags `[1]`, `[2]`, etc. replace the bracket key:

```mdx
## References <a id="references"></a>

<section class="refs">
  <ol>
    <li><span class="tag">[1]</span> Galanter, P. (2016). Generative art theory. In C. Paul (Ed.), *A Companion to Digital Art* (pp. 146-180). Wiley-Blackwell. <a href="https://doi.org/10.1002/9781118475249.ch8" target="_blank" rel="noopener">doi:10.1002/9781118475249.ch8</a></li>
    <li><span class="tag">[2]</span> Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. ISBN 978-0-262-03561-3.</li>
  </ol>
</section>
```

In-text citations in MDX use the numeric tag inline (e.g., "(Galanter, 2016) [1]") or simply reference the number in superscript/brackets — see `src/content/lessons/1.1.1.mdx` for the canonical pattern.

---

## Citation Quality Checklist

- [ ] All claims cited: Every factual statement has a source
- [ ] Credible sources: Academic journals, respected books, official docs
- [ ] Recent sources: Prefer last 5-10 years (except historical context)
- [ ] Diverse sources: Mix of papers, textbooks, and documentation
- [ ] Accessible: Include DOIs and URLs where available
- [ ] Proper formatting: APA 7th edition exactly
- [ ] Context notes (optional): `[Seminal overview of deep learning]` after citations

---

## Common Mistakes

**Wrong**: Uncited "Did You Know?" fact

> Neural networks can have billions of parameters!

**Correct**: Cited fact

> GPT-3 has 175 billion parameters (Brown et al., 2020).

---

*Extracted from CLAUDE.md. Citation rules are content-format-agnostic — only the rendering syntax differs between v1 RST and v2 MDX.*
