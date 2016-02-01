/*
    Author: Michael Rechenberg

    Phaser Visualizer code for mm22

    This will draw the sprites for each of the characters using
    the JSON from the server (however we decide to send it).
    The server is responsible for making sure the movements are valid.

    A good reference for Phaser things: https://leanpub.com/html5shootemupinanafternoon/read
    Phaser website: http://phaser.io/

    New JSON will be sent every (1/2) second???
    
    Loose JSON??? What does this mean exactly.

    I'll have a shit ton of JSON and I'll update the vis at the time
        at my discretion (popping from a queue).

    
    TODO: Keep track of Asset Lists
    TODO: Figure out how the movement system will be translated
        into the JSON, a.k.a what calculation will be done by the
        visualizer (Jack, Eric)
    TODO: Stats screen layout
    TODO: Create queue for JSON to be parsed
    TODO: Remove any dummy data/variables/JSON


    -----MAP----
    120x120 pixel quadrants, w/ pillars
    I'll have to fit all of the characters in each quadrant
    ----/MAP----

    What Will Happen For Every Bit Of JSON
        Update Stats Screen Data
        Move Characters
        Add any spells/actions to the spells group w/ addSpell()
        Release any of the spells with releaseSpells()





*/

//Number of milliseconds until the next bit of JSON will be processed
//  and the visualizer is updated
var TIME_TO_NEXT_UPDATE = 500;

//Number of milliseconds allowed for each spell to be tweened
//  i.e. to move from caster to target 
var TIME_FOR_SPELLS = 500;

//designates how many a sprite for every unit of movement designated by the JSON
//This is unecessary if the JSON sends the absolute position of characters
var MOVEMENT_PIXELS = 5;


//Constants to define Phaser's width and height

//Width of the game, where sprites will be drawn
var GAME_WIDTH = 600;
//Height of the game
var GAME_HEIGHT = 600;
//Width of the space where to display the stats of each player
var STAT_WIDTH = 400;

//Constant to define the x and y coords of any sprite we load
//  but don't want to be visible
var OFF_SCREEN = -500;


//Reference to the core game object
//If you want to use game.debug in the render() function, you need to set
//  Phaser.AUTO to Phaser.CANVAS (the renderer)
var game = new Phaser.Game(GAME_WIDTH + STAT_WIDTH, GAME_HEIGHT, Phaser.AUTO,
 'phaser-game', { preload: preload, create: create, update: update});

//Variables to refer to the characters by
var star;
var dude1;
var dude2;

//TODO: Have all characters added to this group instead
//  of indiv names like star or dude2
//Group containing all of the characters we want to use
var characters;

//Group containing all the spells to be cast
var spells;


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
    //background image
    game.load.image('desertBackground', 'assets/desert-tiles.png');

    //sprites for the characters
    game.load.image('star', 'assets/20x20star.png');
    game.load.image('dude1', 'assets/dude1.png');
    game.load.image('dude2', 'assets/dude2.png');
    game.load.image('spell1', 'assets/spell1.png');
    
    //log success
    console.log("preload() complete");
}

//add the assets to the game 
function create () {
    //enable physics, only needed to move multiple spells
    //game.physics.startSystem(Phaser.Physics.ARCADE);

    //set background image
    var desertBackground = game.add.sprite(0, 0, 'desertBackground');

    //create group for spells
    spells = game.add.group();

    //create group for characters
    characters = game.add.group();

    //dummy characters
    star = characters.create(game.world.centerX, game.world.centerY, 'star');
    dude1 = characters.create(100, 450, 'dude1');
    dude2 = characters.create(200, 100, 'dude2');

    //enable click input for characters
    characters.setAll('inputEnabled', true);
    characters.callAll('events.onInputDown.add', 'events.onInputDown', 
        changeStatScreen);


    //log success
    console.log("create() complete");
}

//called every frame, roughly 60 frames per second
function update () {

    //Uncomment this if you want to move one step at a time with a mouse click
    game.input.onTap.add(moveCharacters, this);

    //Uncomment this if you want to move the characters by pushing the up arrow
    if(game.input.keyboard.isDown(Phaser.Keyboard.UP)){
        moveCharacters();
    }

}

//DEBUG ONLY WORKS IF RENDERER IS SET TO Phaser.CANVAS
//If you delete this function (it is not needed for the game to work)
//  then you must remove the 'render' key/value from the core game
//  object's constructor
// function render(){
//     console.log("star is at x: " + star.x + ", y: ", star.y);
//     console.log("dude1 is at x: " + dude1.x + ", y", dude1.y);
//     console.log("dude2 is at x: " + dude2.x + ", y", dude2.y);
// }


//TODO: Modify this to work w/ the JSON given by the server
//TODO: Modify this so that characters move to quadrants and 
//  auto fit into each one (allow multiple characters to be in 
//  a quadrant without overlapping)
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
    //dummy function to show casting spells
    addSpell(dude2, dude1, "spell1");
    addSpell(dude1, star, "spell1");
    addSpell(star, dude2, "spell1");
    releaseSpells();
}

//List to keep track of caster and target
var spellList = [];

/*
    Adds a spell to the spells group.
    Call releaseSpells() to move all the spell sprites
        to their respective targets.
    If you want a spell to target the caster (self-heal, 
        self-buff), just set caster and target to the
        same value.

    caster--the sprite of the character casting the spell
    target--the sprite of the charcter targetted by the spell
    spellName--string of the key denoting the sprite of a 
        certain spell.
*/
function addSpell(caster, target, spellName){
    spells.create(caster.x, caster.y, spellName);
    spellList.push({"caster" : caster, "target" : target});
}

/*
    Releases all the spells that were added by addSpell(),
    moving each spell sprite to their respective target.
    This function clears both spellList and the spells group.
*/
function releaseSpells(){
    //Go through all the spells in the spells group
    //  and tween them to their targets
    var index = spellList.length-1;
    var tween;
    while(index >= 0){
        //get the last child
        var currentSpell = spells.getChildAt(index);
        //moves the spell
        tween = game.add.tween(currentSpell).to({x: spellList[index].target.x, 
            y: spellList[index].target.y}, TIME_FOR_SPELLS, null, true);
        index--;
    }
    
    //cleanup
    spellList = [];
    tween.onComplete.add(removeSpells, this);
    function removeSpells(){
        spells.removeAll(true, false);
    };
    
}

//TODO: Have this display the stats of each sprite on the
//  side bar
function changeStatScreen(){
    console.log("changeStatScreen called");
}



