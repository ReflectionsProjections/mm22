
var GAME_WIDTH = 800;
var GAME_HEIGHT = 600;

//designates how many a sprite will move with each update
var MOVEMENT_PIXELS = 5;
var game = new Phaser.Game(GAME_WIDTH, GAME_HEIGHT, Phaser.AUTO, '', { preload: preload, create: create, update: update});
var cursors;
var star;

function preload () {
   game.load.image('star', 'assets/20x20star.png');
    game.load.image('logo', 'phaser.png');
    game.load.image('desertBackground', 'assets/desert-tiles.png');
    
}

function create () {

    var desertBackground = game.add.sprite(0, 0, 'desertBackground');
    star = game.add.sprite(game.world.centerX, game.world.centerY, 'star');
  
}

function update () {


    //Uncomment this if you want to move around with the keyboard
    //This is difficult if you want to see one movement at a time

    // if(game.input.keyboard.isDown(Phaser.Keyboard.LEFT)){
    //     star.x-=MOVEMENT_PIXELS;
    // }
    // else if(game.input.keyboard.isDown(Phaser.Keyboard.RIGHT)){
    //     star.x += MOVEMENT_PIXELS;
    // }
    // else if (game.input.keyboard.isDown(Phaser.Keyboard.UP)){
    //     star.y -= MOVEMENT_PIXELS;
    // }
    // else if (game.input.keyboard.isDown(Phaser.Keyboard.DOWN)){
    //     star.y += MOVEMENT_PIXELS;
    // }

    //Uncomment this if you want to move one step at a time with a mouse click
    //game.input.onTap.add(onTap, this);
}


// function onTap(pointer, doubleTap) {
//     star.x -= MOVEMENT_PIXELS;
//     //star.y += MOVEMENT_PIXELS;
// }