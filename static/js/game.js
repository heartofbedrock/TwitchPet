const socket = io();

let state = { hunger: 50, happiness: 50, health: 50, sleeping: false };
let textBars;

const config = {
    type: Phaser.AUTO,
    width: 400,
    height: 400,
    backgroundColor: '#222',
    parent: 'game',
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

const game = new Phaser.Game(config);

function preload() {
    this.load.spritesheet('pet', 'sprites/pet.png', { frameWidth: 100, frameHeight: 100 });
}

function create() {
    this.pet = this.add.sprite(200, 200, 'pet', 0);
    textBars = this.add.text(10, 10, '', { font: '16px Arial', fill: '#fff' });
    socket.on('pet_update', (s) => {
        state = s;
        updateBars();
        updateFrame();
    });
    socket.on('action_performed', (data) => {
        this.tweens.add({ targets: this.pet, scale: 1.2, duration: 100, yoyo: true });
    });
}

function update() {}

function updateBars() {
    textBars.setText(`Hunger: ${state.hunger}\nHappiness: ${state.happiness}\nHealth: ${state.health}`);
}

function updateFrame() {
    if (state.sleeping) {
        this.pet.setFrame(3);
    } else if (state.hunger > 80) {
        this.pet.setFrame(2);
    } else if (state.happiness > 70) {
        this.pet.setFrame(1);
    } else {
        this.pet.setFrame(0);
    }
}
