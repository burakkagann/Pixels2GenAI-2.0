/** Link into the thesis PDF at a printed page number (the PDF has 11 front-matter pages). */
export const THESIS_PDF = '/research/thesis.pdf';
export const thesisHref = (printedPage: number) => `${THESIS_PDF}#page=${printedPage + 11}`;
