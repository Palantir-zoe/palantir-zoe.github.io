/* KaTeX compilation for the PRML reading note. Static build, no remote assets. */
const fs = require('fs');
const path = require('path');
const katex = require(path.join(__dirname, '..', '.runtime', 'katex-0.16.25.min.js'));
let source = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { source += chunk; });
process.stdin.on('end', () => {
  const expressions = JSON.parse(source);
  const result = expressions.map((item, index) => {
    try {
      return katex.renderToString(item.tex, {
        displayMode: item.display,
        throwOnError: true,
        output: 'htmlAndMathml',
        strict: 'ignore',
        trust: false,
      });
    } catch (error) {
      throw new Error(`Formula ${index + 1}: ${item.tex}\n${error.message}`);
    }
  });
  process.stdout.write(JSON.stringify(result));
});
