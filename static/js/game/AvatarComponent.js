import { BaseElem } from './templ/baseelem.js';
import { html } from './templ/template.js';



export class AvatarComponent extends BaseElem {
    static observedAttributes = ["size", "src", "status", "radius", "statusborder", "statustext"];
    constructor() {
        super();
        this.size = 50;
        this.src = "";
        this.status = "none";
        this.radius = "circle";
        this.statusborder = false;
        this.statustext = false;
    }

    imgElem = (hasStatus, statusColor) => {
        let border = "";
        if (hasStatus && this.statusborder)
            border = `border border-${this.size > 100 ? "3" : "2"} border-${statusColor}`
        return html`
        <img
            class="rounded-${this.radius} object-fit-cover ${border}"
            alt="avatar"
            src="${this.src}"
            width="${this.size ?? ""}"
            height="${this.size ?? ""}"
        />
    `}

    svgElem = (hasStatus, statusColor) => {
        let border = "";
        if (hasStatus && this.statusborder)
            border = `border border-${this.size > 100 ? "3" : "2"} border-${statusColor}`
        return html`
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="${this.size ?? "0"}"
                height="${this.size ?? "0"}"
                fill="currentColor"
                class="bi bi-person-circle rounded-${this.radius} ${border}"
                viewBox="0 0 16 16"
            >
                <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0" />
                <path
                    fill-rule="evenodd"
                    d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1"
                />
            </svg>
    `}

    renderStatus = (hasStatus, statusColor) => {
        if (!hasStatus)
            return "";
        if (this.statustext)
            return html`
                <span class="position-absolute top-100 start-50 translate-middle badge rounded-pill text-bg-${statusColor}">
                    ${this.status}
                </span>`;
        if (this.statusborder)
            return ""
        return html`
            <span
                class="text position-absolute p-2 border border-light rounded-circle bg-${statusColor}"
                style="transform: translate(${Number(this.size) * 0.6}px, ${Number(this.size) * -0.1}px);"
            ></span>
        `
    }

    render() {
        const hasStatus = (this.status === "online" || this.status === "offline");
        const statusColor = this.status === "online" ? "success" : this.status === "offline" ? "danger" : "";

    return html`
        <span class="d-flex align-items-center">
            <slot name="before"></slot>
            <span
                class="position-relative d-flex flex-column"
                style="width:${this.size ?? "0"}px; height:${this.size ?? "0"}px;"
            >
                ${this.src ? this.imgElem(hasStatus, statusColor) : this.svgElem(hasStatus, statusColor)}
                ${this.renderStatus(hasStatus, statusColor)}
                
            </span>
            <slot name="after"></slot>
        </span>
    `
    }
}
customElements.define("avatar-component", AvatarComponent);




export const renderAvatar = (id, username, avatar, status, side, classes) => {
    return html`
        <a href="/profile/${id}"
            class="${classes} link-body-emphasis link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover"
        >
            <avatar-component size="40" src="${avatar}" statusborder status="${status}" radius="circle" >
                <span class="m-2 text-truncate" slot="${side ? side : "after"}">${username}</span>
            </avatar-component>
        </a>
    `
}
