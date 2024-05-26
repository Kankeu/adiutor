/**
 * ==============================================
 * All credit for X-Frame-Bypass to https://github.com/niutech/x-frame-bypass
 * ==============================================
 */

customElements.define('x-frame-bypass', class extends HTMLIFrameElement {
    static get observedAttributes() {
        return ['src']
    }
    constructor () {
        super()
    }
    attributeChangedCallback () {
        this.load(this.src)
    }
    connectedCallback () {
        this.sandbox = '' + this.sandbox || 'allow-forms allow-modals allow-pointer-lock allow-popups allow-popups-to-escape-sandbox allow-presentation allow-same-origin allow-scripts allow-top-navigation-by-user-activation' // all except allow-top-navigation
    }
    load (url, options) {
        if (!url || !url.startsWith('http'))
            throw new Error(`X-Frame-Bypass src ${url} does not start with http(s)://`)
        this.srcdoc = `<html>
<head>
	<style>
	.loader {
		position: absolute;
		top: calc(50% - 25px);
		left: calc(50% - 25px);
		width: 50px;
		height: 50px;
		background-color: #333;
		border-radius: 50%;  
		animation: loader 1s infinite ease-in-out;
	}
	@keyframes loader {
		0% {
		transform: scale(0);
		}
		100% {
		transform: scale(1);
		opacity: 0;
		}
	}
	</style>
</head>
<body>
	<div class="loader"></div>
</body>
</html>`
        this.fetchProxy(url, options, 0).then(res => res.text()).then(data => {
            if (data)
                this.srcdoc = data.replace(/<head([^>]*)>/i, `<head$1>
	<base href="${url}">
	<script>
	// X-Frame-Bypass navigation event handlers
	document.addEventListener('click', e => {
		if (frameElement && document.activeElement && document.activeElement.href) {
			e.preventDefault()
			frameElement.load(document.activeElement.href)
		}
	})
	document.addEventListener('submit', e => {
		if (frameElement && document.activeElement && document.activeElement.form && document.activeElement.form.action) {
			e.preventDefault()
			if (document.activeElement.form.method === 'post')
				frameElement.load(document.activeElement.form.action, {method: 'post', body: new FormData(document.activeElement.form)})
			else
				frameElement.load(document.activeElement.form.action + '?' + new URLSearchParams(new FormData(document.activeElement.form)))
		}
	})
	</script>`)
        }).catch(e => console.error('Cannot load X-Frame-Bypass:', e))
    }
    async fetchProxy (url, options, i) {
        const proxies = (options || {}).proxies || [
            'https://cors.io/?',
            'https://jsonp.afeld.me/?url=',
            'https://yacdn.org/proxy/',
            'https://api.codetabs.com/v1/proxy/?quest=',
            'https://cors-anywhere.herokuapp.com/',
            'https://proxy.megatunger.com/'
        ]
        try{
            const controller = new AbortController();
            setTimeout(()=>controller.abort(),3000)
            const res = await fetch(proxies[i%(2* proxies.length)] + url, {...(options??{}),signal:controller.signal})
            return res
        }catch (e) {
            console.error(e)
            if (i%(2* proxies.length) === proxies.length - 1)
            {
                throw Error("X-Frame-Bypass max trial reached!!!")
            }
            return await this.fetchProxy(url, options, i + 1)
        }
    }
}, {extends: 'iframe'})