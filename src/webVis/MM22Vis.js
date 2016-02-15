/*
    Author: Michael Rechenberg

    Phaser Visualizer code for mm22

    This will draw the sprites for each of the characters using
    the JSON from the server (however we decide to send it) and
    any spells casted by any players.
    The server is responsible for making sure the movements are valid.

    Assumes that there are 6 players total (3 on each team)

    A good reference for Phaser things: https://leanpub.com/html5shootemupinanafternoon/read
    Phaser website: http://phaser.io/

    The execution of Phaser functions is as follows:

        preload()
        create()
        update()
        render()

    preload() and create() only run once, while update() and render()
    run every frame
    render() is usually not needed, but is good for debugging

    
    Loose JSON??? What does this mean exactly.

    The server will send a lot of JSON, but it will be added
     to a queue and the front element will be dequeued every
     time the turn is displayed onto the screen, as determined by
     TIME_TO_NEXT_UPDATE.

    
    TODO: Keep track of Asset Lists
    TODO: Figure out how the movement system will be translated
        into the JSON, a.k.a what calculation has to be done by the
        visualizer (Jack, Eric, Asaf)
    TODO: Stats screen layout
        Menu to select player
        Select a player on click
    TODO: Create queue for JSON to be parsed
    TODO: Remove any dummy data/variables/JSON


    -----MAP----
    A 5x5 configuration with 120x120 pixel spaces for "quadrants"
    Each quadrant has a 3x3 configuration, with each element 
        a 40x40 pixel space
    Characters will be placed within each quadrant such that
        all 6 characters can fit in one quadrant at one time

    x ----->
    y 
    |
    |
    V

    ----/MAP----

    What Will Happen For Every Bit Of JSON
        Update Stats Screen Data
        Move Characters
            Have each character fit in the next "quadrant"
                Can characters move w/in a quadrant???
        Add any spells/actions to the spells group w/ addSpell()
        Release any of the spells with releaseSpells()





*/

//Number of milliseconds until the next bit of JSON will be processed
//  and the visualizer is updated
var TIME_TO_NEXT_UPDATE = 1000;

//Number of milliseconds allowed for each spell to be tweened
//  i.e. to move from caster to target 
var TIME_FOR_SPELLS = 500;



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
//The width is 1000 pixels (GAME_WIDTH + STATWIDTH) and the height is 
//  600 pixels (GAME_HEIGHT)
var game = new Phaser.Game(GAME_WIDTH + STAT_WIDTH, GAME_HEIGHT, Phaser.AUTO,
 'phaser-game', { preload: preload, create: create, update: update});


//Reference to the game's timer
var timer;

//Reference to the game's graphics class
var graphics;


//width and height of a character's sprite, in pixels
var CHARACTER_DIMENSION = 40;

//width and height of a quadrant, in pixels
//The each quadrant is accessed by multiplying QUADRANT_DIMENSION  
//  by 0, 1, 2, 3, or 4
var QUADRANT_DIMENSION = 120;





//Group containing all of the characters we want to use
var characters;

//Arrays that hold the players on each team
var teamA = [];
var teamB = [];

//Handles on all of the sprites of all the characters
var playerOne;
var playerTwo;
var playerThree;
var playerFour;
var playerFive;
var playerSix;



//Group containing all the spells to be cast on one turn
var spells;

//Object to contain all of the handles to Phaser text objects 
//  and other things relevant to the stats screen
//TODO: Have CurrentPlayer allow for iteration to redesignate AttributeStrings' text 
//  in changeStatScreen
var statScreen = {
    //Keeps track of the name of the player currently being tracked
    "CharacterName" : null,
    "AttributeStrings" : {
        "Health" : null,
        "Damage" : null,
        "AbilityPower" : null,
        "AttackRange" : null,
        "AttackSpeed" : null,
        "Armor" : null,
        "MovementSpeed" : null
    }
};
//constant of Y-position of where the text of attributes will be positioned
//  relative to this coordinate
var ATTRIBUTE_STRINGS_Y = 300;

//dummyJSON for testing
var dummyPlayer = {
    "stats" : {
            "Health"        : 500,
            "Damage"        : 50,
            "AbilityPower" : 50,
            "AttackRange"   : 5,
            "AttackSpeed"   : 2,
            "Armor"         : 10,
            "MovementSpeed" : 5,
            "Abilities"     : [ 1 ]
    }

};




//load our assets
function preload () {
    //background image
    game.load.image('background', 'assets/grid-background.jpg');

    //TODO: add code so each player has the sprite corresponding to 
    //  their class
    //sprites for the characters
    game.load.image('playerOne', 'assets/star40x40.png');
    game.load.image('playerTwo', 'assets/dude1-40x40.png');
    game.load.image('playerThree', 'assets/dude2-40x40.png');
    game.load.image('playerFour', 'assets/star40x40.png');
    game.load.image('playerFive', 'assets/dude1-40x40.png');
    game.load.image('playerSix', 'assets/dude2-40x40.png')
    game.load.image('spell1', 'assets/spell1.png');
    
    //log success
    console.log("preload() complete");
}

//add the assets to the game and make them visible
//initate any functions to be called on a looping schedule
function create () {
    //enable physics, so far not necessary
    //game.physics.startSystem(Phaser.Physics.ARCADE);

    //set background image
    var background = game.add.sprite(0, 0, 'background');

    //create group for spells
    spells = game.add.group();

    //create group for characters
    characters = game.add.group();
    //Add all players to the characters group at their initial locations
    //TODO: add all characters to their intitial locations according to JSON
    //TODO: Let participants choose names for their character???
    playerOne = characters.create(2 * QUADRANT_DIMENSION, 1 * QUADRANT_DIMENSION, 'playerOne');
    playerOne.name = "playerOne";
    playerTwo = characters.create(3 * QUADRANT_DIMENSION, 1 * QUADRANT_DIMENSION, 'playerTwo');
    playerTwo.name = "playerTwo";
    playerThree = characters.create(2* QUADRANT_DIMENSION, 2*QUADRANT_DIMENSION, 'playerThree');
    playerThree.name = "playerThree";
    playerFour = characters.create(3* QUADRANT_DIMENSION, 3*QUADRANT_DIMENSION, 'playerFour');
    playerFour.name = "playerFour";
    playerFive = characters.create(4* QUADRANT_DIMENSION, 2*QUADRANT_DIMENSION, 'playerFive');
    playerFive.name = "playerFive";
    playerSix = characters.create(3* QUADRANT_DIMENSION, 2*QUADRANT_DIMENSION, 'playerSix');
    playerSix.name = "playerSix";

    //TODO: Code to add each player to teamA or teamB, use the JSON




    //enable input for all character sprites
    characters.setAll('inputEnabled', true);
    //When input is detected (currently only clicking on a sprite is detected)
    // changeStatScreen is called by the sprite's corresponding player variable
    //Pass the variable of the calling character sprite to
    // changeStatScreen() 
    characters.callAll('events.onInputDown.add', 'events.onInputDown', 
        changeStatScreen, this);

    //Have the timer call all of the following functions every
    //  TIME_TO_NEXT_UPDATE milliseconds
    game.time.events.loop(TIME_TO_NEXT_UPDATE, moveCharactersQuadrantAbsolute, this);
    game.time.events.loop(TIME_TO_NEXT_UPDATE, updateStatScreen, this);

    //create handle for game graphics 
    //All things drawn by graphics have x and y origin
    //  at 0, 0
    graphics = game.add.graphics();
    graphics.beginFill(HEALTH_BAR_COLOR);
    healthBar = graphics.drawRect(HEALTH_BAR_X, HEALTH_BAR_Y, 
        STAT_WIDTH - 20, HEALTH_BAR_HEIGHT);
    console.log(healthBar);
    graphics.endFill();

    //add the character's name to the stats screen
    statScreen.characterName = game.add.text(GAME_WIDTH + 10, 10, "PLAYER ONE", {font: "4em Arial", fill: "#ff944d"});

    //Set up the strings for each player's stats in the Stat Screen
    //TODO: Replace dummyPlayer.stats.X with stats of the JSON
    //TODO: Pad the strings so the numbers all align nicely
    var attrStrSpacing = 35;
    statScreen.AttributeStrings.MovementSpeed = game.add.text(GAME_WIDTH + 20, ATTRIBUTE_STRINGS_Y, 
        "Movement Speed:" + dummyPlayer.stats.Health, {font: "3em Arial", fill: "#ffa366"});
    statScreen.AttributeStrings.Damage = game.add.text(GAME_WIDTH + 20, ATTRIBUTE_STRINGS_Y + attrStrSpacing, 
        "Damage:        " + dummyPlayer.stats.Damage, {font: "3em Arial", fill: "#ffa366"});
    statScreen.AttributeStrings.AbilityPower = game.add.text(GAME_WIDTH + 20, ATTRIBUTE_STRINGS_Y + 2*attrStrSpacing, 
        "Ability Power: " + dummyPlayer.stats.AbilityPower, {font: "3em Arial", fill: "#ffa366"});
    statScreen.AttributeStrings.AttackRange = game.add.text(GAME_WIDTH + 20, ATTRIBUTE_STRINGS_Y + 3*attrStrSpacing,
        "Attack Range:  " + dummyPlayer.stats.AttackRange, {font: "3em Arial", fill: "#ffa366"});
    statScreen.AttributeStrings.AttackSpeed = game.add.text(GAME_WIDTH + 20, ATTRIBUTE_STRINGS_Y + 4*attrStrSpacing,
        "Attack Speed:  " + dummyPlayer.stats.AttackSpeed, {font: "3em Arial", fill: "#ffa366"});
    statScreen.AttributeStrings.Armor = game.add.text(GAME_WIDTH + 20, ATTRIBUTE_STRINGS_Y + 5*attrStrSpacing,
        "Armor:         " + dummyPlayer.stats.Armor, {font: "3em Arial", fill: "#ffa366"});





    //Display the word 'Health' underneath the health bar
    game.add.text(GAME_WIDTH + (STAT_WIDTH/2) -30, HEALTH_BAR_Y + HEALTH_BAR_HEIGHT + 10, "Health", {fill: "#33cc33", font: "2em Arial"});


    //log success
    console.log("create() complete");
}

//called every frame, roughly 60 frames per second
function update () {


    //Adds callback to event listener for clicking
    //Uncomment this if you want to move one step at a time with a mouse click
    //game.input.onTap.add(moveCharactersQuadrantAbsolute, this);

    // //Uncomment this if you want to move the characters by pushing the up arrow
    // if(game.input.keyboard.isDown(Phaser.Keyboard.UP)){
    //     //moveCharacters();
    //     moveCharactersQuadrant();
    // }

}


//-------------END OF PHASER CODE-------------------//





















//List to keep track of caster and target of spells
var spellList = [];


//TODO: Have spells go to "center" of sprite
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
    //add the spell sprite to the spells group
    //  and add the corresponding spell's sprite 
    //  to the caster's current position
    spells.create(caster.x, caster.y, spellName);
    //add the caster and target to the spellList array
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
        //get the child, starting at the end of the group
        //  and moving towards the first element
        var currentSpell = spells.getChildAt(index);
        //moves the spell on the screen, takes TIME_FOR_SPELLS amount of milliseconds
        tween = game.add.tween(currentSpell).to({x: spellList[index].target.x + 10, 
            y: spellList[index].target.y + 10}, TIME_FOR_SPELLS, null, true);
        index--;
    }
    
    //cleanup
    spellList = [];
    tween.onComplete.add(removeSpells, this);
    function removeSpells(){
        spells.removeAll(true, false);
    };
    
}

//Dummy JSON to test moveCharactersQuadrant()
//number of quadrants to move in the x or y direction
var dummyMovement = {
    "playerOne" : 
    {
        "x" : 1,
        "y" : 1
    },
    "playerTwo" : 
    {
        "x" : 0,
        "y" : 1
    },
    "playerThree" : 
    {
        "x" : 1,
        "y" : 0
    },
    "playerFour" : 
    {
        "x" : 0,
        "y" : -1
    },
    "playerFive" : 
    {
        "x" : -1,
        "y" : 0
    },
    "playerSix" : 
    {
        "x" : 0,
        "y" : 0
    }
};

//----------------Code for Movemement---------------//


//Represents the map wih a 5x5 array of "tuples"
//Each "tuple" is (row,column) that is available for
//  the next sprite to be inserted
//Access this array in the following way:
//  nextQuadrantSpaceAvailable[quadrantRow][quadrantColumn][0 or 1]
//      0 denotes a row within the quadrant
//      1 denotes a column within the quadrant
//  
//  column ---->
//  row
//   |
//   |
//   V
//

var nextQuadrantSpaceAvailable = [
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],

];


/**
    Moves a character from one quadrant to another.
    
    Moves using JSON that gives displacement of each player
    in relation to their old quadrant.
        If a player has an x of 1 and y of -1, they will move
        one box to the right and up one box.


    If multiple characters are in the same quadrant,
      space them out so each character sprite can be 
      visible. 

    Each quadrant is defined to be 120x120 pixels

    NOTE: Does not check to see if the move is valid
        (does not check if the character will move off of the map,
        into a pillar)

    TODO: Use jQuery's .each method to clean up this code
*/
function moveCharactersQuadrant(){
    //TODO: Use absolute position if JSON from server gives that

    //reset nextQuadrantSpaceAvailable so all spaces are available
    for(var i = 0; i < nextQuadrantSpaceAvailable.length; i++){
        for(var j = 0; j < nextQuadrantSpaceAvailable[i].length; j++){
            nextQuadrantSpaceAvailable[i][j][0] = 0;
            nextQuadrantSpaceAvailable[i][j][1] = 0;
        } 
    }

    for(var k in dummyMovement){
        //marks the coordinates of where the player will be after moving
        var newQuadrantRow = 0;
        var newQuadrantCol = 0;
        switch(k){
            case "playerOne":
                //calculate the player's new destination
                newQuadrantCol = (playerOne.x + dummyMovement[k]["x"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                newQuadrantRow = (playerOne.y + dummyMovement[k]["y"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                //move them into the quadrant at the top-left corner
                playerOne.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerOne.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerOne.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerOne.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            case "playerTwo":
                newQuadrantCol = (playerTwo.x + dummyMovement[k]["x"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                newQuadrantRow = (playerTwo.y + dummyMovement[k]["y"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                //move them into the quadrant
                playerTwo.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerTwo.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerTwo.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerTwo.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            case "playerThree":
                newQuadrantCol = (playerThree.x + dummyMovement[k]["x"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                newQuadrantRow = (playerThree.y + dummyMovement[k]["y"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                //move them into the quadrant
                playerThree.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerThree.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerThree.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerThree.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            case "playerFour":
                newQuadrantCol = (playerFour.x + dummyMovement[k]["x"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                newQuadrantRow = (playerFour.y + dummyMovement[k]["y"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                //move them into the quadrant
                playerFour.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerFour.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerFour.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerFour.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            case "playerFive":
                newQuadrantCol = (playerFive.x + dummyMovement[k]["x"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                newQuadrantRow = (playerFive.y + dummyMovement[k]["y"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                //move them into the quadrant
                playerFive.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerFive.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerFive.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerFive.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            case "playerSix":
                newQuadrantCol = (playerSix.x + dummyMovement[k]["x"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                newQuadrantRow = (playerSix.y + dummyMovement[k]["y"] * QUADRANT_DIMENSION)/QUADRANT_DIMENSION;
                //move them into the quadrant
                playerSix.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerSix.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerSix.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerSix.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            default:
                break;
        }
    }




}


//Uses assignment from the JSON rather than a +=, so use this if
//  the JSON gives ABSOLUTE position rather than relative displacement
function moveCharactersQuadrantAbsolute(){

   //reset nextQuadrantSpaceAvailable so all spaces are available
    for(var i = 0; i < nextQuadrantSpaceAvailable.length; i++){
        for(var j = 0; j < nextQuadrantSpaceAvailable[i].length; j++){
            nextQuadrantSpaceAvailable[i][j][0] = 0;
            nextQuadrantSpaceAvailable[i][j][1] = 0;
        } 
    }
    //have the sprites move to a random location (x,y) = ((0-4),(0-4))
    randomizeMovement();


    for(var k in dummyMovement){
        //marks the coordinates of where the player will be after moving
        var newQuadrantRow = 0;
        var newQuadrantCol = 0;
        newQuadrantCol = dummyMovement[k]["x"];
        newQuadrantRow = dummyMovement[k]["y"];
        switch(k){
            case "playerOne":
                //move them into the quadrant at the top-left corner
                playerOne.x = dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerOne.y = dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerOne.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerOne.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                break;
            case "playerTwo":
                //move them into the quadrant
                playerTwo.x = dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerTwo.y = dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerTwo.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerTwo.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                break;
            case "playerThree":
                //move them into the quadrant
                playerThree.x = dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerThree.y = dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerThree.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerThree.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                break;
            case "playerFour":
                //move them into the quadrant
                playerFour.x = dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerFour.y = dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerFour.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerFour.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                break;
            case "playerFive":
                //move them into the quadrant
                playerFive.x = dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerFive.y = dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerFive.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerFive.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                break;
            case "playerSix":
                //move them into the quadrant
                playerSix.x = dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerSix.y = dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerSix.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerSix.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                break;
            default:
                break;
        }
        //update the column part of the "tuple"
        nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
        //if the column is 3, move to the next row
        if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
            nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
            nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
        }
    }
    addSpell(playerThree, playerTwo, "spell1");
    addSpell(playerTwo, playerOne, "spell1");
    addSpell(playerOne, playerThree, "spell1");
    releaseSpells();
}

//Helper function for moveCharactersQuadrantTest()
//Randomizes the x and y of dummyLocation to an integer [0-4]
function randomizeMovement(){
    for (var k in dummyMovement){
        //ensure the property is not part of the prototype
        if(dummyMovement.hasOwnProperty(k)){
             for(var l in dummyMovement[k]){
                dummyMovement[k][l] = Math.floor(Math.random()*5);
            }
        }
       
    }
}



//-----------------Code for Stats Screen---------------------//



/**
    Changes which character's stats are displayed
        in the stats screen.
*/
function changeStatScreen(character){
    console.log("changeStatScreen called");
    console.log(character.name);
    statScreen.CharacterName = character.name;
    //clear all graphics drawn from the graphics reference
    graphics.clear();
    //updates the name of the character whose stats are displayed
    //NOTE: Does not check to see if name will fit yet
    statScreen.characterName.setText((character.name).toUpperCase());
    updateHealthBar(character);


}

/**
    Called to update all the graphics associated with the 
        Stats Screen.
    If the character selected has changed, call changeStatScreen()
*/
function updateStatScreen(character){
    graphics.clear();
    updateHealthBar(character);
}


//Reference to the health bar of the stats screen
var healthBar;
var HEALTH_BAR_COLOR = 0x33CC33;
var HEALTH_BAR_X = GAME_WIDTH + 10;
var HEALTH_BAR_Y = 100;
var HEALTH_BAR_HEIGHT = 20;

/**
    Redraws the Health Bar
    Currently it sets to health bar to a random value,
        but later it will set to the health of the current
        player.
*/
function updateHealthBar(character){
    //redraw the health bar
    graphics.beginFill(HEALTH_BAR_COLOR);
    healthBar = graphics.drawRect(HEALTH_BAR_X, HEALTH_BAR_Y, 
        (Math.floor(Math.random() * STAT_WIDTH)), 
        HEALTH_BAR_HEIGHT);
    graphics.endFill();
}



