/*
    Michael Rechenberg

    Example Phaser code for mm22

    This will draw the sprites for each of the characters using
    the JSON from the server (however we decide to send it).
    The server is responsible for making sure the movements are valid.

    A good reference for Phaser things: https://leanpub.com/html5shootemupinanafternoon/read

    Phaser website: http://phaser.io/

*/
var GAME_WIDTH = 800;
var GAME_HEIGHT = 600;

//designates how many a sprite for every unit of movement designated by the JSON
var MOVEMENT_PIXELS = 5;

//Reference to the core game object
//TODO: Set Phaser.CANVAS to Phaser.AUTO if not debugging
var game = new Phaser.Game(GAME_WIDTH, GAME_HEIGHT, Phaser.CANVAS, '', 
    { preload: preload, create: create, update: update, render: render});

//used for cursor input, is not needed if client interactivity
//  is not necessary
var cursors;

//Variables to refer to the characters by
var star;
var dude1;
var dude2;


//dummy JSON data for updating the location of the characters
//Format:
//
//  characterName--The name of the character you want to update
//      x--The number of MOVEMENT_PIXELS to move in the x-direction
//      y--The number of MOVEMENT_PIXELS to move in the y-direction
//
var locationUpdate = {
    "star": 
    {
        "x": 1, 
        "y": -1
    },
    "dude1" : 
    {
        "x": 0, 
        "y" : 3
    },
    "dude2": 
    {
        "x": -2,
        "y": 0
    }
};

//load our assets
function preload () {
    //background
    game.load.image('desertBackground', 'assets/desert-tiles.png');

    //sprites for the characters
    game.load.image('star', 'assets/20x20star.png');
    game.load.image('dude1', 'assets/dude1.png');
    game.load.image('dude2', 'assets/dude2.png');
    
    
}

//add the assets to the game 
function create () {

    var desertBackground = game.add.sprite(0, 0, 'desertBackground');
    star = game.add.sprite(game.world.centerX, game.world.centerY, 'star');
    dude1 = game.add.sprite(550, 450, 'dude1');
    dude2 = game.add.sprite(200, 100, 'dude2');
  
}

//call every frame, roughly 60 frames per second?
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
    game.input.onTap.add(moveCharacters, this);

    //Uncomment this if you want to move the characters by pushing the up arrow
    if(game.input.keyboard.isDown(Phaser.Keyboard.UP)){
        moveCharacters();
    }

}

//DEBUG ONLY WORKS IF RENDERER IS SET TO Phaser.CANVAS
//I would use game.debug function calls but they don't work for
// some reason :P
//If you delete this function (it is not needed for the game to work)
//  then you must remove the 'render' key/value from the core game
//  object's constructor
function render(){
    console.log("star is at x: " + star.x + ", y: ", star.y);
    console.log("dude1 is at x: " + dude1.x + ", y", dude1.y);
    console.log("dude2 is at x: " + dude2.x + ", y", dude2.y);
}



function moveCharacters(){
     for (var k in locationUpdate){
        //switch statement to know which character to update
        // by updating the corresponding sprite variable's x and 
        // y fields.
        //The characters move in multiples of MOVEMENT_PIXELS
        switch(k){
            case "star":
                star.x += locationUpdate[k]["x"] * MOVEMENT_PIXELS;
                star.y += locationUpdate[k]["y"] * MOVEMENT_PIXELS;
                break;
            case "dude1":
                dude1.x += locationUpdate[k]["x"] * MOVEMENT_PIXELS;
                dude1.y += locationUpdate[k]["y"] * MOVEMENT_PIXELS;
                break;
            case "dude2":
                dude2.x += locationUpdate[k]["x"] * MOVEMENT_PIXELS;
                dude2.y += locationUpdate[k]["y"] * MOVEMENT_PIXELS;
                break;
            default:
                break;
        }
        //randomize the movement data [-2, 2]
        locationUpdate[k]["x"] = Math.floor((Math.random()* 3));
        if(Math.floor(Math.random()*2) == 0){
            locationUpdate[k]["x"] *= -1;
        }
        locationUpdate[k]["y"] = Math.floor((Math.random()* 3));
        if(Math.floor(Math.random()*2) == 0){
            locationUpdate[k]["y"] *= -1;
        }
    }
}