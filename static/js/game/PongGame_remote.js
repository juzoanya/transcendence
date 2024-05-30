import { BaseElem } from './templ/baseelem.js';
import { html } from './templ/template.js';
import { dirs } from './templ/nodes.js';

import { AvatarComponent, renderAvatar } from './AvatarComponent.js';
import { GameHubRemote } from './gameHub_remote.js';


/**
 *
 * @param {HTMLElement} obsElem
 * @param {number} aspectRatio
 * @param {(newW: number, newH: number) => void} cb
 * @returns
 */
function useCanvasSizes(obsElem, aspectRatio, cb) {
    if (!obsElem) throw new Error("undefined wrapper Element");
    if (aspectRatio <= 0) throw new Error("invalid aspect Ratio");
    if (!cb) throw new Error("undefined callback");
    let newW, newH;
    const elemRect = obsElem.getBoundingClientRect();
    const myObserver = new ResizeObserver(entries => {

        // console.log("window: ", {width: window.innerWidth, height: window.innerHeight});
        // console.log("elemRect: ", elemRect);
        // console.log("rect: ", entries[0].contentRect);
        newW = entries[0].contentRect.width;
        newH = entries[0].contentRect.height;
        const calcW = Math.trunc(newH / aspectRatio);
        const calcH = Math.trunc(newW * aspectRatio);
        if (calcH > newH) {
            cb(calcW, newH);
        } else {
            cb(newW, calcH);
        }
        // // console.log("newW: ", newW);
        // // console.log("newH: ", newH);
       
    });
    myObserver.observe(obsElem);
    let disconnected = false;
    return (() => {
        if (disconnected) return ;
        myObserver.disconnect();
        disconnected = true;
    });
}

export class GameModalRemote extends BaseElem {

    static observedAtrributes = ["id"]

    constructor() {
        super(false, false);
        
        this.props.currentGameData = undefined;
        this.currentGame = undefined;
    }
    #aspectRatio = 0.5;
    #closeObs;

    /** @type {HTMLCanvasElement} */
    #canvas;
    /** @type {HTMLDivElement} */
    #wrapper;
  
    disconnectedCallback() {
        super.disconnectedCallback();
        this.#closeObs();
        this.currentGame?.terminateGame();
    }

    onColorChange() {
        // this.#sendWorker(pMsg.changeColor);
    }

    #workerMessage = "";
    /** @param {MessageEvent | ErrorEvent} ev  */
    onMessage(type, ev) {
        if (ev instanceof ErrorEvent || type === "error" || type === "messageerror")
            this.currentGame?.terminateGame();
        if (!(ev instanceof MessageEvent)) return ;
        
        this.#workerMessage = ev.data;
        super.requestUpdate();
    }

    #gamesocket;
    #modalIsOpen = false;
    async onModalShown() {
        // console.log("on modal shown");
      
        this.#modalIsOpen = true;
        super.requestUpdate();
        this.currentGame = await GameHubRemote.startGame("pong", this.#canvas, this.props.game_data, this.onMessage.bind(this));
        this.#closeObs = useCanvasSizes(this.#wrapper, this.#aspectRatio, (newW, newH) => {
            this.#canvas.style.width = newW + "px";
            this.#canvas.style.height = newH + "px";
            this.currentGame?.resizeCanvas(newW, newH, window.devicePixelRatio);
        });
    }

    onModalHide() {
        this.#modalIsOpen = false;
        super.requestUpdate();
        this.#closeObs();
        this.currentGame?.terminateGame();
    }

    /** @param {import('../../services/types.js').GameScheduleItem | undefined} gameData */
    renderHeader = (gameData) => html`
        <div class="modal-header">
            <h1 class="modal-title fs-5" id="gameModal-label">Match:</h1>
            <div class="w-100 d-flex align-items-center justify-content-evenly">
                <div class="d-flex align-items-center p-1 border border-2 border-success rounded-3" @click=${(ev)=>{ev.stopPropagation(); ev.preventDefault()}}>
                    ${renderAvatar(gameData?.player_one.id, gameData?.player_one.username, gameData?.player_one.avatar, "", "before", "")}
                    <span class="fs-1 px-3">${this.currentGame?.scorePlayerOne}</span>
                </div>
                <p class="p-2 m-0 fs-3 text-body-emphasis">
                    VS
                </p>
                <div class="d-flex align-items-center p-1 border border-2 border-danger rounded-3" @click=${(ev)=>{ev.stopPropagation(); ev.preventDefault()}}>
                    <span class="fs-1 px-3">${this.currentGame?.scorePlayerOne}</span>
                    ${renderAvatar(gameData?.player_two.id, gameData?.player_two.username, gameData?.player_two.avatar, "", "after", "")}
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
    `

    renderFooter = () => html`
        <div class="modal-footer">
            <button @click=${()=>{this.currentGame?.startGame()}} type="button" class="btn btn-primary">start game</button>
            <button @click=${()=>{this.currentGame?.quitGame()}} type="button" class="btn btn-success">quit game</button>
            <button @click=${()=>{this.currentGame?.pauseGame()}} type="button" class="btn btn-warning">pause game</button>
            <button @click=${()=>{this.currentGame?.continueGame()}} type="button" class="btn btn-info">continue game</button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary">Save changes</button>
        </div>
    `

    render() {
        /** @type {import('../../services/types.js').GameScheduleItem | undefined} */
        const gameData = this.props.game_data;
        return html`
            <div
                @hide.bs.modal=${ (ev) => { this.onModalHide() } }
                @shown.bs.modal=${ (ev) => { this.onModalShown() } }
                class="modal fade" id="${this.id}-id" tabindex="-1" aria-labelledby="gameModal-label" aria-hidden="true" data-bs-keyboard="false">
                <div class="modal-dialog modal-fullscreen">
                    <div class="modal-content">
                        ${this.renderHeader(gameData)}
                        <div class="modal-body">
                            ${!this.#modalIsOpen ? "" : html`
                                <div ${(elem)=> {this.#wrapper = elem}} class="w-100 h-100">
                                    <canvas ${(elem)=> {this.#canvas = elem}} ></canvas>
                                </div>
                            `}
                        </div>
                        ${this.renderFooter()}
                    </div>
                </div>
            </div>
            
    `;
    }
}
window.customElements.define("game-modal-remote", GameModalRemote);


