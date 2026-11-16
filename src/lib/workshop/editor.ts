/**
 * Code editor for workshop code cells: CodeMirror 6, self-hosted through npm
 * (exact pinned versions, SEC-20), loaded only on workshop lesson pages.
 *
 * - Python highlighting, line numbers, undo, auto-indent with 4 spaces.
 * - Ctrl+Enter / Cmd+Enter runs the cell.
 * - Tab indents; Esc then Tab leaves the editor (CodeMirror's escape hatch), so
 *   keyboard users are never trapped.
 * - The blank "___" is highlighted: it marks where the learner's answer goes.
 * - Colours come from the site's tokens (CSS variables), so light and dark work.
 */
import { EditorState } from '@codemirror/state';
import {
  Decoration,
  EditorView,
  MatchDecorator,
  ViewPlugin,
  type DecorationSet,
  type ViewUpdate,
  drawSelection,
  highlightActiveLine,
  keymap,
  lineNumbers,
} from '@codemirror/view';
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands';
import { HighlightStyle, indentUnit, syntaxHighlighting, bracketMatching } from '@codemirror/language';
import { python } from '@codemirror/lang-python';
import { tags } from '@lezer/highlight';

// Token colours: the site's palette, via CSS variables (no hex here).
const highlight = HighlightStyle.define([
  { tag: [tags.keyword, tags.controlKeyword, tags.operatorKeyword, tags.definitionKeyword], color: 'var(--c3)', fontWeight: '600' },
  { tag: [tags.string, tags.special(tags.string)], color: 'var(--c1)' },
  { tag: [tags.number, tags.bool, tags.null], color: 'var(--c2)' },
  { tag: [tags.comment, tags.lineComment], color: 'var(--fg-3)', fontStyle: 'italic' },
  { tag: [tags.function(tags.variableName), tags.function(tags.definition(tags.variableName))], color: 'var(--fg)', fontWeight: '600' },
  { tag: tags.definition(tags.variableName), color: 'var(--fg)' },
]);

const theme = EditorView.theme({
  '&': {
    fontFamily: 'var(--mono)',
    fontSize: '15px',
    lineHeight: '1.75',
    backgroundColor: 'var(--code-surface)',
    color: 'var(--fg)',
  },
  '.cm-content': { caretColor: 'var(--fg)', padding: '10px 0' },
  '.cm-gutters': {
    backgroundColor: 'var(--code-surface)',
    color: 'var(--fg-4)',
    borderRight: '1px solid var(--code-border)',
  },
  '.cm-activeLine': { backgroundColor: 'var(--bg-2)' },
  '.cm-activeLineGutter': { backgroundColor: 'var(--bg-2)', color: 'var(--fg-2)' },
  '&.cm-focused': { outline: '3px solid var(--fg)', outlineOffset: '-3px' },
  '.cm-selectionBackground, &.cm-focused .cm-selectionBackground, ::selection': {
    backgroundColor: 'var(--c2-tint)',
  },
  '.cm-blank': {
    backgroundColor: 'var(--ws-yellow)',
    color: 'var(--ws-on-yellow)',
    outline: '2px solid var(--fg)',
    borderRadius: '0',
  },
});

// Highlight every "___" blank.
const blankDecorator = new MatchDecorator({ regexp: /___/g, decoration: Decoration.mark({ class: 'cm-blank' }) });
const blanks = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;
    constructor(view: EditorView) {
      this.decorations = blankDecorator.createDeco(view);
    }
    update(update: ViewUpdate) {
      this.decorations = blankDecorator.updateDeco(update, this.decorations);
    }
  },
  { decorations: (plugin) => plugin.decorations },
);

export interface CellEditor {
  getCode(): string;
  setCode(code: string): void;
  focus(): void;
}

/**
 * Replace the plain <textarea> fallback with an editor. Without JavaScript (or
 * if this fails) the textarea stays and still shows the code.
 */
export function createEditor(textarea: HTMLTextAreaElement, label: string, onRun: () => void): CellEditor {
  const runKeys = keymap.of([
    { key: 'Mod-Enter', run: () => { onRun(); return true; }, preventDefault: true },
  ]);
  const view = new EditorView({
    state: EditorState.create({
      doc: textarea.value,
      extensions: [
        lineNumbers(),
        history(),
        drawSelection(),
        highlightActiveLine(),
        bracketMatching(),
        indentUnit.of('    '),
        EditorState.tabSize.of(4),
        runKeys,
        keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
        python(),
        syntaxHighlighting(highlight),
        theme,
        blanks,
        EditorView.contentAttributes.of({ 'aria-label': label }),
      ],
    }),
  });
  textarea.hidden = true;
  textarea.after(view.dom);
  return {
    getCode: () => view.state.doc.toString(),
    setCode: (code) => view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: code } }),
    focus: () => view.focus(),
  };
}
