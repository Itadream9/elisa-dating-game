import { Howl } from 'howler';

const sfx = {
    click: new Howl({ src: ['https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'], volume: 0.5 }), // Generic Click
    messageSent: new Howl({ src: ['https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3'], volume: 0.4 }), // Soft pop
    messageReceived: new Howl({ src: ['https://assets.mixkit.co/active_storage/sfx/2354/2354-preview.mp3'], volume: 0.5 }), // Notification
    error: new Howl({ src: ['https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3'], volume: 0.5 }), // Error Buzz
    win: new Howl({ src: ['https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3'], volume: 0.8 }), // Success chord
    bgm: null
};

export const playSound = (type) => {
    if (sfx[type]) {
        sfx[type].play();
    }
};

export const playAudioUrl = (url) => {
    const sound = new Howl({
        src: [url],
        html5: true, // Force HTML5 Audio for streaming if needed
        format: ['mp3', 'wav'],
        volume: 1.0
    });
    sound.play();
}
