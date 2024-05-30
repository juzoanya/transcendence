
/**
 * @typedef {Object} GameSettings
 * @property {number} speed
 * @property {number} maxScore
 */

/**
 * @typedef {Object} WorkerDataInit
 * @property {HTMLCanvasElement} canvas
 * @property {import('./types_game').GameSettings} gameSettings
 */

/**
 * @typedef {Object} WorkerDataResize
 * @property {number} width
 * @property {number} height
 * @property {number} dpr
 */

/**
 * @typedef {Object} WorkerDataChangeColors
 * @property {string} colorWhite
 * @property {number} colorBlack
 */

/**
 * @typedef {Object} WorkerDataKeyEvent
 * @property {string} keyevent
 * @property {string} key
 */

/**
 * @typedef {Object} WorkerDataMouseEvent
 * @property {number} posX
 * @property {number} posY
 */

/**
 * @typedef {Object} WorkerData
 * @property {number} message
 * @property {Object | WorkerDataInit | WorkerDataResize | WorkerDataChangeColors | WorkerDataKeyEvent | WorkerDataMouseEvent} data
 */

/**
 * @typedef {import('./types_game.js').MessageType} MsgType
 */

export const pongMessageTypes = {
    GAME_UPDATE: "game_update",
    INIT_GAME: "init_game",
    START_GAME: "start_game",
    HIDE_BALL: "hide_ball",
    SHOW_BALL: "show_ball",
    GAME_END: "game_end"
}

export const msg_to_worker_remote = {
    init: 0,
    start: 1,
    quit: 2,
    pause: 3,
    continue: 4,
    resize: 5,
    changeColor: 6,
    update_pos: 7,
    hide_ball: 8,
    show_ball: 9,
    create: 10,
};

export const msg_to_main = {
    player_1_score : 10,
    player_1_win : 20,
    player_2_score : 30,
    player_2_win : 40,
    draw_timeout : 50,
    error: 100
};