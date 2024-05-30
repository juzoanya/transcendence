import { LiveTemplate, Template, TemplateAsLiteral, html }  from "./template.js";

/**
 * @typedef {Object} AttrProp
 * @property {string} camel
 * @property {Object} oVal
 */


export class BaseElem extends HTMLElement {

    static #colorModeEvent = "base-elem-toggle-color";
    static #colorModePubSub = new EventTarget();
    static #currentColorMode = "light";
    static toggleColorMode() {
        const ht = document.querySelector("html");
        const newColor = this.#currentColorMode === "light" ? "dark" : "light";
        if (ht) ht.dataset.bsTheme = newColor;
        this.#currentColorMode = newColor;
        const color = BaseElem.#currentColorMode;
        const revColor = color === "light" ? "dark" : "light";
        document.querySelectorAll("button").forEach((btn) => {this.#toggleBtnColor(btn, color, revColor)});
        document.querySelectorAll("input").forEach((btn) => {this.#toggleBtnColor(btn, color, revColor)});
        document.querySelectorAll("a").forEach((btn) => {this.#toggleBtnColor(btn, color, revColor)});
        this.#colorModePubSub.dispatchEvent(new CustomEvent(this.#colorModeEvent, {detail: newColor}));
    }
    static #changeDocumentBtnColors() {
        const color = BaseElem.#currentColorMode;
        const revColor = color === "light" ? "dark" : "light";
        document.querySelectorAll("button").forEach((btn) => {this.#toggleBtnColor(btn, color, revColor)});
        document.querySelectorAll("input").forEach((btn) => {this.#toggleBtnColor(btn, color, revColor)});
        document.querySelectorAll("a").forEach((btn) => {this.#toggleBtnColor(btn, color, revColor)});
    }

    #changeBtnColors(color, revColor, toggleTheme) {
        if (this.shadowRoot) {
            Array.from(this.shadowRoot.children).forEach((e)=>{
                if(e instanceof HTMLElement) {
                    if (toggleTheme) e.dataset.bsTheme = color;
                        BaseElem.#toggleBtnColor(e, color, revColor);
                }
                e.querySelectorAll("button").forEach((btn) => {BaseElem.#toggleBtnColor(btn, color, revColor)});
                e.querySelectorAll("input").forEach((btn) => {BaseElem.#toggleBtnColor(btn, color, revColor)});
                e.querySelectorAll("a").forEach((btn) => {BaseElem.#toggleBtnColor(btn, color, revColor)});
            });
        }
    }

    static #toggleBtnColor = (elem, color, revColor) => {
        if (elem.classList.contains(`btn-outline-${color}`)) {
            elem.classList.remove(`btn-outline-${color}`);
            elem.classList.add(`btn-outline-${revColor}`);
        } else if (elem.classList.contains(`btn-${color}`)) {
            elem.classList.remove(`btn-${color}`);
            elem.classList.add(`btn-${revColor}`);
        }
    };
    #adjustBtnColors() {
        const color = BaseElem.#currentColorMode;
        const revColor = color === "light" ? "dark" : "light";
        this.#changeBtnColors(color, revColor, false);
    }

    /** @param {CustomEvent} ev  */
    #changeColorMode(ev) {
        const color = ev.detail;
        const revColor = color === "light" ? "dark" : "light";
        /** @param {HTMLElement} elem */
        this.#changeBtnColors(color, revColor, true);
        this.onColorChange();
    }

    onColorChange() {}


    /** @type {Map<string, AttrProp>} */
    #attrPropMapRef;
    #initAttrPropMap() {
        // @ts-ignore
        const obs = this.constructor.observedAttributes;
        if (this.#attrPropMapRef !== undefined || !(obs instanceof Array))
            return;
        // @ts-ignore
        this.constructor.___attrPropMap___ = new Map();
        // @ts-ignore
        this.#attrPropMapRef = this.constructor.___attrPropMap___;
        obs.forEach((attr) => {
            const propName = BaseElem.toCamel(attr);
            
            this.#attrPropMapRef.set(attr, { camel: propName, oVal: null });
        });
        
    }
    get isConnected() {
        return (this.#isConnected);
    }

    #attributePropMap;
    #mapMyAttr(name, nVal, oVal) {
        if (this.#attrPropMapRef === undefined) this.#initAttrPropMap();
        const pObj = this.#attrPropMapRef.get(name);
        if (!pObj) return;
       
        if (nVal === oVal) {
            return ;
        }
       
        pObj.oVal = this[pObj.camel];
        if (typeof this[pObj.camel] === "boolean") {
            this[pObj.camel] = nVal === null ? false : true;
        } else if (typeof this[pObj.camel] === "number") {
            this[pObj.camel] = Number(nVal);
        } else if (typeof this[pObj.camel] === "object") {
            this[pObj.camel] = JSON.parse(nVal);
        } else {
            this[pObj.camel] = String(nVal);
        }
       
        this.onAttributeChange(name);
        if (this.#isConnected)
            this.update();
       
    }

    requestUpdate() {
        // console.log("request Update");
        console.log("request Update");
        if (this.#isConnected) {
            // console.log("is connected! update")
            this.update();
        }
    }

    /** @param {Object | undefined} [shadowOption=undefined]  */
    constructor(useBootstrap=true, useShadow=true, shadowOption=undefined) {
        super();

        // @ts-ignore
        this.#attrPropMapRef = this.constructor.___attrPropMap___;
        if (useShadow) {
            const shadow = this.attachShadow(shadowOption ?? { mode: "open" });
            shadow.adoptedStyleSheets = [];
            // @ts-ignore
            if (this.constructor.styles instanceof Array) shadow.adoptedStyleSheets.push(...this.constructor.styles);

            this.root = shadow;
        } else {
            this.root = this;
        }

        const setFunc = (obj, prop, value) => {
            // console.log("setFunc: ")
            // console.log("prop obj: ", obj)
            // console.log("propname: ", prop)
            // console.log("propvalue: ", value)
            obj[prop] = value;
            this.requestUpdate();
            return true;
        }
        this.__props__ = {
            _children: ""
        };
        this.props = new Proxy(this.__props__, { set: setFunc });

        /** @type {TemplateAsLiteral | Array<TemplateAsLiteral> | string | number | boolean} */
        this._children = "";

        // this.props = new Proxy(this.#props, )
        
    }

    

    onSlotChange(e) {
        this.update();
    }


    #isConnected = false;
    connectedCallback() {
        if (this.#attrPropMapRef === undefined) this.#initAttrPropMap();
        this.update();
        this.#isConnected = true;
        this.shadowRoot?.addEventListener("slotchange", this.onSlotChange.bind(this));
        BaseElem.#colorModePubSub.addEventListener(BaseElem.#colorModeEvent, this.#changeColorMode.bind(this));

        // // // console.log("MY KEYS: ", Object.keys(this))
        Object.keys(this).forEach((prop)=>{
            const elem = this[prop];
        })
        
    }

    disconnectedCallback() {
        this.#isConnected = false;
        if (this.#templ) {
            this.#templ.unMountMe();
        }
        this.shadowRoot?.removeEventListener("slotchange", this.onSlotChange.bind(this));
        Object.keys(this).forEach((prop)=>{
            const elem = this[prop];
        })
        BaseElem.#colorModePubSub.removeEventListener(BaseElem.#colorModeEvent, this.#changeColorMode.bind(this));
        // console.log("BASE ELEM DISCONNECT!!!!", this)
    }
    onAttributeChange(attributeName) {}


    attributeChangedCallback(name, oVal, nVal) {
        this.#mapMyAttr(name, nVal, oVal);
    }

    /** @type {LiveTemplate} */
    #templ;
    update() {
        const res = this.render();
        
        if (res === null || res  === undefined)
            return ;
        if (this.#templ === undefined) {
            this.#templ = Template.getInstance(res.strings)
            this.#templ.mountMe( this.root, null, res.values);
        } else {
            this.#templ.update(res.values);
            // // console.log("UPDATE COMPLETED: ", this);
        }
        this.#adjustBtnColors();
        BaseElem.#changeDocumentBtnColors();
    }
    
    /** @returns {TemplateAsLiteral | null}  */
    render() {
        return (null);
    }
   
    static toCamel = (s) => s.replace(/-./g, (x) => x[1].toUpperCase());
    static toKebap = (s) =>
        s.replace(
            /[A-Z]+(?![a-z])|[A-Z]/g,
            ($, ofs) => (ofs ? "-" : "") + $.toLowerCase()
        );
}






    
        
// // @ts-ignore
// if (this.constructor.styles instanceof Array) {
//     /** @type {Array<CSSStyleSheet>} */
//     // @ts-ignore
//     const styles = this.constructor.styles;
    
//     if (!styles.every((elem) => elem instanceof CSSStyleSheet))
//         throw new Error("only constructed stylesheets allowed");
    
//     if (!useBootstrap || (useBootstrap && styles.includes(bootstrapstyles))) {
//         shadow.adoptedStyleSheets = styles;
//     } else if (useBootstrap) {
// //         // // console.log("USE BOOTSTRAP STYLES")
//         shadow.adoptedStyleSheets = [bootstrapstyles, ...styles]
// //         // // console.log("adopted: ", shadow.adoptedStyleSheets)
//     }
//     // shadow.adoptedStyleSheets = this.constructor.styles;
// } else if (useBootstrap) {
//     shadow.adoptedStyleSheets = [bootstrapstyles]
// }

// import { LiveTemplate, Template, TemplateAsLiteral, html }  from "../lib_templ/v1/template.js";
// // import { bootstrapstyles } from '../assets/bootstrapcss.js';
// import { BaseReactive } from "./services/pubsub_new.js";

//         import("./styles/iconsStyleSheet.js").then((module) => {
// //             console.log("module");
// //             console.log(module);
//         })

// // import { iconFontStyleSheet } from './styles/iconsStyleSheet.js';

// // const iconFontStyleSheet = await import("./styles/iconsStyleSheet.js");

// // import { iconStyleSheet } from '../app.js';


// /**
//  * @typedef {Object} AttrProp
//  * @property {string} camel
//  * @property {Object} oVal
//  */

// // document.adoptedStyleSheets = [...document.adoptedStyleSheets, bootstrapstyles];

// export class BaseElem extends HTMLElement {

//     static #stylesInited = false;
//     static #initStyles() {
//         // if (this.#stylesInited) return ;
// //         // console.log("initstyles")
//         // import("./styles/iconsStyleSheet.js").then((module) => {
// //         //     console.log("module");
// //         //     console.log(module);
//         // })

//         // customElements.

//         this.#stylesInited = true;
//     }


//     /** @type {Map<string, AttrProp>} */
//     #attrPropMapRef;
//     #initAttrPropMap() {
//         // @ts-ignore
//         const obs = this.constructor.observedAttributes;
//         if (this.#attrPropMapRef !== undefined || !(obs instanceof Array))
//             return;
//         // @ts-ignore
//         this.constructor.___attrPropMap___ = new Map();
//         // @ts-ignore
//         this.#attrPropMapRef = this.constructor.___attrPropMap___;
//         obs.forEach((attr) => {
//             const propName = BaseElem.toCamel(attr);
            
//             this.#attrPropMapRef.set(attr, { camel: propName, oVal: null });
//         });
        
//     }
//     get isConnected() {
//         return (this.#isConnected);
//     }

//     #attributePropMap;
//     #mapMyAttr(name, nVal, oVal) {
//         if (this.#attrPropMapRef === undefined) this.#initAttrPropMap();
//         const pObj = this.#attrPropMapRef.get(name);
//         if (!pObj) return;
       
//         if (nVal === oVal) {
//             return ;
//         }
       
//         pObj.oVal = this[pObj.camel];
//         if (typeof this[pObj.camel] === "boolean") {
//             this[pObj.camel] = nVal === null ? false : true;
//         } else if (typeof this[pObj.camel] === "number") {
//             this[pObj.camel] = Number(nVal);
//         } else if (typeof this[pObj.camel] === "object") {
//             this[pObj.camel] = JSON.parse(nVal);
//         } else {
//             this[pObj.camel] = String(nVal);
//         }
       
//         this.onAttributeChange(name);
//         if (this.#isConnected)
//             this.update();
       
//     }

//     #setStyles(shadow, useBootstrap) {
//         // @ts-ignore
//         // if (this.constructor.styles instanceof Array) {
//         //     /** @type {Array<CSSStyleSheet>} */
//         //     // @ts-ignore
//         //     const styles = this.constructor.styles;
            
//         //     if (!styles.every((elem) => elem instanceof CSSStyleSheet))
//         //         throw new Error("only constructed stylesheets allowed");
           
//         //     if (!useBootstrap || (useBootstrap && styles.includes(bootstrapstyles))) {
//         //         shadow.adoptedStyleSheets = styles;
//         //     } else if (useBootstrap) {
// //         //         // // console.log("USE BOOTSTRAP STYLES")
//         //         shadow.adoptedStyleSheets = [bootstrapstyles, ...styles]
// //         //         // // console.log("adopted: ", shadow.adoptedStyleSheets)
//         //     }
//         //     // shadow.adoptedStyleSheets = this.constructor.styles;
//         // } else if (useBootstrap) {
//         //     shadow.adoptedStyleSheets = [bootstrapstyles]
//         // }
//     }

//     requestUpdate() {
//         this.update();
//     }

//     // #props = {};
//     // #handlePropChange = {
//     //     set(target, property, value, receiver) {
//     //         if (target[property] !== value)
//     //         return Reflect.set(target, property, value, receiver);
//     //     }
//     // }

//     /** @param {Object | undefined} [shadowOption=undefined]  */
//     constructor(useBootstrap=true, useShadow=true, shadowOption=undefined) {
//         super();

//         if (BaseElem.#stylesInited === false) BaseElem.#initStyles();

//         // @ts-ignore
//         this.#attrPropMapRef = this.constructor.___attrPropMap___;
//         if (useShadow) {
//             const shadow = this.attachShadow(shadowOption ?? { mode: "open" });
//             this.#setStyles(shadow, useBootstrap);
//             this.root = shadow;
//         } else {
//             this.root = this;
//         }

//         // this.props = new Proxy(this.#props, )
        
//     }
//     onSlotChange(e) {
//         this.update();
//     }


//     #isConnected = false;
//     connectedCallback() {
//         if (this.#attrPropMapRef === undefined) this.#initAttrPropMap();
//         this.update();
//         this.#isConnected = true;
//         this.shadowRoot?.addEventListener("slotchange", this.onSlotChange.bind(this));

// //         // // console.log("MY KEYS: ", Object.keys(this))
//         Object.keys(this).forEach((prop)=>{
//             const elem = this[prop];
//             if (elem instanceof BaseReactive)
//                 elem.__onConnected();
//         })
        
//     }
//     disconnectedCallback() {
//         this.#isConnected = false;
//         if (this.#templ) {
//             this.#templ.unMountMe();
//         }
//         this.shadowRoot?.removeEventListener("slotchange", this.onSlotChange.bind(this));
//         Object.keys(this).forEach((prop)=>{
//             const elem = this[prop];
//             if (elem instanceof BaseReactive)
//                 elem.__onDisconnected();
//         })
//     }
//     onAttributeChange(attributeName) {}


//     attributeChangedCallback(name, oVal, nVal) {
//         this.#mapMyAttr(name, nVal, oVal);
//     }

//     /** @type {LiveTemplate} */
//     #templ;
//     update() {
//         const res = this.render();
//         if (res === null || res  === undefined)
//             return ;
//         if (this.#templ === undefined) {
//             this.#templ = Template.getInstance(res.strings)
//             this.#templ.mountMe( this.root, null, res.values);
//         } else {
//             this.#templ.update(res.values);
//         }
//     }
    
//     /** @returns {TemplateAsLiteral | null}  */
//     render() {
//         return (null);
//     }
   
//     static toCamel = (s) => s.replace(/-./g, (x) => x[1].toUpperCase());
//     static toKebap = (s) =>
//         s.replace(
//             /[A-Z]+(?![a-z])|[A-Z]/g,
//             ($, ofs) => (ofs ? "-" : "") + $.toLowerCase()
//         );
// }
