
const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const assert = require('assert');

// Load files
const html = fs.readFileSync('index.html', 'utf8');
const css = fs.readFileSync('styles.css', 'utf8');
const jsCode = fs.readFileSync('script.js', 'utf8');

// Create DOM from HTML
const dom = new JSDOM(html, {
    runScripts: 'dangerously',
    resources: 'usable'
});

// Inject CSS (optional – for style testing if needed)
const styleElement = dom.window.document.createElement('style');
styleElement.textContent = css;
dom.window.document.head.appendChild(styleElement);

// Inject and execute the script
const scriptElement = dom.window.document.createElement('script');
scriptElement.textContent = jsCode;
dom.window.document.body.appendChild(scriptElement);

// Short delay to allow event listeners to attach
setTimeout(() => {
    try {
        // Test initial state
        const heading = dom.window.document.getElementById('greeting');
        assert.strictEqual(heading.textContent, 'Hello', 'Initial heading text is not "Hello"');

        // Simulate click on button
        const button = dom.window.document.getElementById('btn');
        button.click();

        // Test updated state
        assert.strictEqual(heading.textContent, 'Welcome, Judge0!', 'Heading did not update after click');

        console.log('All tests passed!');
        process.exit(0);
    } catch (err) {
        console.error('Test failed:', err.message);
        process.exit(1);
    }
}, 100);