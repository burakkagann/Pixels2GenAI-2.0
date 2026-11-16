// @ts-check
/**
 * Plain-language explanations for Python errors in code cells (03e §6).
 * Returns plain text only; the page puts it into the DOM with textContent.
 * Names from the error are quoted, never interpreted as markup.
 */

/**
 * @param {string} last  the last line of the traceback, e.g. "NameError: name 'x' is not defined"
 * @returns {string}
 */
export function explainError(last) {
  const line = String(last ?? '');
  if (/name '___' is not defined/.test(line) || /^SyntaxError.*___/.test(line)) {
    return 'Replace ___ with your own code. The blank marks where your answer goes.';
  }
  const name = line.match(/NameError: name '(\w+)' is not defined/);
  if (name) {
    return `Python doesn't know '${name[1]}' yet. Is it spelled the same as where it was made? Every cell starts fresh, so create it in this cell too.`;
  }
  if (/IndentationError|TabError/.test(line)) return "The spaces at the start of a line don't line up. Lines inside a 'for' or 'def' need the same indent.";
  if (/SyntaxError/.test(line)) return "Python couldn't read a line. Check brackets, commas and colons near the line it mentions.";
  if (/broadcast|shapes? .*(?:not aligned|mismatch)|operands could not/.test(line)) {
    return "Two arrays have different shapes, so Python can't combine them number by number. Print their .shape to compare.";
  }
  if (/IndexError/.test(line)) return 'That position is outside the array. Rows and columns start at 0 and stop one before the size.';
  if (/ZeroDivisionError/.test(line)) return 'Something was divided by zero.';
  if (/TypeError/.test(line)) return 'A value has the wrong type for this operation, for example a list where a number is expected.';
  if (/ValueError/.test(line)) return 'A value has the right type but the wrong content. The message above says which.';
  if (/KeyboardInterrupt|Stopped/.test(line)) return 'The run was stopped.';
  if (/SetupError/.test(line)) return 'Python could not start. Check your internet connection and run again.';
  return 'Python stopped with an error. Its last line says what went wrong.';
}
