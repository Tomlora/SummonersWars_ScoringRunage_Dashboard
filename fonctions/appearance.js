// Streamlit 1.65 host theme protocol. V2 components run in the app window.
// Only fixed palettes are sent, to this window's exact origin. No React/DOM
// internals, synthetic events, config mutation or page reload are needed.
export default function ({ parentElement, data }) {
    const focused = parentElement.querySelector('input:focus')?.value;
    const storageKey = 'sw-dashboard-appearance-v1';
    const status = parentElement.querySelector('[role="status"]');
    const choices = parentElement.querySelector('.choices');
    parentElement.querySelector('legend').textContent = data.legend;
    let choice = 'custom';
    let persistent = true;
    try {
        const saved = localStorage.getItem(storageKey);
        if (Object.hasOwn(data.palettes, saved)) choice = saved;
    } catch { persistent = false; }
    let timer;
    const inputs = [];

    function matches(palette) {
        const app = document.querySelector('[data-testid="stApp"]');
        const color = palette.backgroundColor.match(/\w\w/g).map(v => parseInt(v, 16));
        return app && getComputedStyle(app).backgroundColor === `rgb(${color.join(', ')})`;
    }

    function apply(key) {
        choice = key;
        const palette = data.palettes[key];
        for (const input of inputs) input.checked = input.value === key;
        try { localStorage.setItem(storageKey, key); }
        catch { persistent = false; }
        if (!matches(palette)) {
            window.postMessage({stCommVersion: 1, type: 'SET_CUSTOM_THEME_CONFIG', themeInfo: palette}, window.location.origin);
        }
        status.textContent = data.applying;
        clearTimeout(timer);
        let attempts = 0;
        function confirm() {
            if (matches(palette)) {
                // Update custom surfaces only after native widgets accept the
                // palette, avoiding unreadable mixed colors if a host rejects it.
                const root = document.documentElement.style;
                for (const [name, value] of Object.entries({
                    background: palette.backgroundColor, surface: palette.secondaryBackgroundColor,
                    border: palette.borderColor, text: palette.textColor, primary: palette.primaryColor,
                    muted: key === 'white' ? '#526277' : key === 'black' ? '#b8b8b8' : '#aebed2',
                })) root.setProperty(`--sw-${name}`, value);
                status.textContent = persistent ? data.saved : data.temporary;
            } else if (++attempts < 40) {
                timer = setTimeout(confirm, 50);
            } else {
                status.textContent = data.error;
            }
        }
        timer = setTimeout(confirm, 50);
    }

    choices.replaceChildren();
    for (const [key, palette] of Object.entries(data.palettes)) {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'radio'; input.name = 'sw-appearance'; input.value = key;
        input.addEventListener('change', () => apply(key));
        inputs.push(input);
        const swatch = document.createElement('span');
        swatch.className = 'swatch'; swatch.style.background = palette.backgroundColor;
        swatch.setAttribute('aria-hidden', 'true');
        label.append(input, swatch, document.createTextNode(data.labels[key]));
        choices.append(label);
    }
    apply(choice);
    if (focused) inputs.find(input => input.value === focused)?.focus({preventScroll: true});
    return () => clearTimeout(timer);
}
