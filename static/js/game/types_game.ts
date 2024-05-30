export enum MessageType {
    GAME_UPDATE = "game_update",
    START_GAME = "start_game",
    HIDE_BALL = "hide_ball",
    SHOW_BALL = "show_ball",
    GAME_END = "game_end"
}

// export type MessageType = {
//     GAME_UPDATE: "game_update",
//     START_GAME: "start_game",
//     HIDE_BALL: "hide_ball",
//     SHOW_BALL: "show_ball",
//     GAME_END: "game_end"
// }

export interface GameSettings {
    width: number;
    height: number;
    border_width: number;
    border_height: number;
    paddle_width: number;
    paddle_height: number;
    paddle_speed: number;
    wall_dist: number;
    ball_width: number;
    ball_height: number;
    ball_speed: number;
    point_wait_time: number;
    serve_mode: string; // Assuming serve_mode is a string, e.g., "WINNER", "LOSER", "RANDOM"
    initial_serve_to: string; // Assuming initial_serve_to is a string, e.g., "LEFT", "RIGHT"
    max_score: number;
    tick_duration: number;
}

export interface GameObj {
    x: number;
    y: number;
    dx: number;
    dy: number;
    direction: number | undefined;
}

export interface GameState {
    ball: GameObj
    paddle_left: GameObj
    paddle_right: GameObj
    score: {
        left: number;
        right: number;
    };
}

// export interface GameState {
//     ball: {
//         x: number;
//         y: number;
//         dx: number;
//         dy: number;
//     };
//     paddle_left: {
//         x: number;
//         y: number;
//         dx: number;
//         dy: number;
//         direction: number;
//     };
//     paddle_right: {
//         x: number;
//         y: number;
//         dx: number;
//         dy: number;
//         direction: number;
//     };
//     score: {
//         left: number;
//         right: number;
//     };
// }


export interface UpdateGameData {
    state: GameState;
}


export interface GameUpdateMessage {
    msg: MessageType.GAME_UPDATE;
    data: UpdateGameData
}


export interface StartGameData {
    settings: GameSettings;
}

export interface StartGameMessage {
    msg: MessageType.START_GAME;
    data: StartGameData
}

export interface HideBallMessage {
    msg: MessageType.HIDE_BALL;
    data: null;
}

export interface ShowBallMessage {
    msg: MessageType.SHOW_BALL;
    data: {
        state: GameState
    }
}

export interface GameEndMessage {
    msg: MessageType.GAME_END;
    data: {
        winner: string;
    };
}

export type PongMessage = GameUpdateMessage | StartGameMessage | HideBallMessage | ShowBallMessage | GameEndMessage;