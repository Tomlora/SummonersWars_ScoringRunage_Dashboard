import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import assert from 'node:assert/strict';
import test from 'node:test';

const source = readFileSync(new URL('../fonctions/appearance.js', import.meta.url), 'utf8')
    .replace('export default function', 'function render');

function browser(saved, blocked = false) {
    class Element {
        children = []; listeners = {}; style = { setProperty() {} };
        append(...children) { this.children.push(...children); }
        replaceChildren() { this.children = []; }
        addEventListener(event, handler) { this.listeners[event] = handler; }
        setAttribute() {}
    }
    const status = new Element(), choices = new Element(), legend = new Element();
    const parentElement = {querySelector: s => ({'[role="status"]': status, '.choices': choices, legend}[s])};
    const palettes = {
        custom: {base: 1, backgroundColor: '#07111f'},
        white: {base: 0, backgroundColor: '#ffffff'},
        black: {base: 1, backgroundColor: '#000000'},
    };
    let backgroundColor = 'rgb(7, 17, 31)';
    let stored = saved;
    const messages = [];
    const callbacks = [];
    const context = {
        parentElement, data: {palettes, labels: {custom: 'Custom', white: 'White', black: 'Black'},
            legend: 'Theme', saved: 'Saved', temporary: 'Temporary', error: 'Error'},
        localStorage: {
            getItem: () => { if (blocked) throw Error('blocked'); return stored; },
            setItem: (key, value) => { if (blocked) throw Error('blocked'); stored = value; },
        },
        document: {documentElement: new Element(), querySelector: () => ({}),
            createElement: () => new Element(), createTextNode: text => text},
        getComputedStyle: () => ({backgroundColor}),
        setTimeout: callback => callbacks.push(callback), clearTimeout() {},
        window: {location: {origin: 'https://scoringsw.eu'}, postMessage: (message, target) => {
            messages.push({message, target});
            backgroundColor = `rgb(${message.themeInfo.backgroundColor.match(/\w\w/g).map(v => parseInt(v, 16)).join(', ')})`;
        }},
    };
    runInNewContext(source + '\nrender({parentElement, data});', context);
    return {status, messages, callbacks,
        selected: () => choices.children.find(label => label.children[0].checked).children[0].value,
        stored: () => stored,
        change: key => choices.children.find(label => label.children[0].value === key).children[0].listeners.change(),
    };
}

test('custom default, three palettes, native theme messages use only the current origin', () => {
    const b = browser(null);
    assert.equal(b.selected(), 'custom');
    assert.equal(b.messages.length, 0); // already rendered: no theme/rerun loop
    for (const choice of ['white', 'black', 'custom']) {
        b.change(choice);
        assert.equal(b.selected(), choice);
        assert.equal(b.stored(), choice);
        assert.equal(b.messages.at(-1).target, 'https://scoringsw.eu');
        assert.equal(b.messages.at(-1).message.type, 'SET_CUSTOM_THEME_CONFIG');
        assert.equal(b.messages.at(-1).message.stCommVersion, 1);
        b.callbacks.at(-1)();
        assert.equal(b.status.textContent, 'Saved');
    }
    b.change('custom');
    assert.equal(b.messages.length, 3);
});

test('reload restores the preference; independent browsers retain independent choices', () => {
    const first = browser('white'), second = browser('black');
    assert.equal(first.selected(), 'white');
    assert.equal(second.selected(), 'black');
    first.change('custom');
    assert.equal(second.selected(), 'black');
    assert.equal(browser(second.stored()).selected(), 'black');
});

test('unknown stored values cannot become a palette or script', () => {
    for (const value of ['invalid', '__proto__', '<script>']) assert.equal(browser(value).selected(), 'custom');
});

test('blocked storage still permits immediate theme changes', () => {
    const b = browser(null, true);
    b.change('white');
    b.callbacks.at(-1)();
    assert.equal(b.selected(), 'white');
    assert.equal(b.status.textContent, 'Temporary');
});
