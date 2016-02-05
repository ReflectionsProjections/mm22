/*
    Author: Michael Rechenberg

    Phaser Visualizer code for mm22

    This will draw the sprites for each of the characters using
    the JSON from the server (however we decide to send it).
    The server is responsible for making sure the movements are valid.

    A good reference for Phaser things: https://leanpub.com/html5shootemupinanafternoon/read
    Phaser website: http://phaser.io/

    The execution of Phaser functions is as follows:

        preload()
        create()
        update()
        render()

    preload() and create only run once, while update() and render()
    run every frame
    render() is usually not needed, but is good for debugging


    New JSON will be sent every (1/2) second???
    
    Loose JSON??? What does this mean exactly.

    The server will send a lot of JSON, but it will be added
     to a queue and the front element will be dequeued every
     time the turn is displayed onto the screen.

    
    TODO: Keep track of Asset Lists
    TODO: Figure out how the movement system will be translated
        into the JSON, a.k.a what calculation will be done by the
        visualizer (Jack, Eric)
    TODO: Stats screen layout
    TODO: Create queue for JSON to be parsed
    TODO: Remove any dummy data/variables/JSON


    -----MAP----
    A 5x5 configuration with 120x120 pixel spaces for "quadrants"
    Each quadrant has a 3x3 configuration, with each element 
        a 40x40 pixel space
    I'll have to fit all of the characters in each quadrant
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
var TIME_TO_NEXT_UPDATE = 500;

//Number of milliseconds allowed for each spell to be tweened
//  i.e. to move from caster to target 
var TIME_FOR_SPELLS = 500;

//designates how many a sprite for every unit of movement designated by the JSON
//This is unecessary if the JSON sends the absolute position of characters
//Used in moveCharacters only
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
//The width is 1000 pixels (GAME_WIDTH + STATWIDTH) and the height is 
//  600 pixels (GAME_HEIGHT)
var game = new Phaser.Game(GAME_WIDTH + STAT_WIDTH, GAME_HEIGHT, Phaser.AUTO,
 'phaser-game', { preload: preload, create: create, update: update});


//width and height of a character's sprite, in pixels
var CHARACTER_DIMENSION = 40;

//width and height of a quadrant, in pixels
//The each quadrant is accessed by multiplying QUADRANT_DIMENSION  
//  by 0, 1, 2, 3, or 4
var QUADRANT_DIMENSION = 120;

//Boolean array that keeps track of if a sprite is in certain location
//Access section by 





        

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


//load our assets
function preload () {
    //background image
    game.load.image('desertBackground', 'assets/desert-tiles.png');

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

//add the assets to the game 
function create () {
    //enable physics, so far not necessary
    //game.physics.startSystem(Phaser.Physics.ARCADE);

    //set background image
    var desertBackground = game.add.sprite(0, 0, 'desertBackground');

    //create group for spells
    spells = game.add.group();

    //create group for characters
    characters = game.add.group();
    //Add all players to the characters group at their initial locations
    //TODO: add all characters to their intitial locations
    playerOne = characters.create(2 * QUADRANT_DIMENSION, 1 * QUADRANT_DIMENSION, 'playerOne');
    playerTwo = characters.create(3 * QUADRANT_DIMENSION, 1 * QUADRANT_DIMENSION, 'playerTwo');
    playerThree = characters.create(2* QUADRANT_DIMENSION, 2*QUADRANT_DIMENSION, 'playerThree');
    playerFour = characters.create(3* QUADRANT_DIMENSION, 3*QUADRANT_DIMENSION, 'playerFour');
    playerFive = characters.create(4* QUADRANT_DIMENSION, 2*QUADRANT_DIMENSION, 'playerFive');
    playerSix = characters.create(3* QUADRANT_DIMENSION, 2*QUADRANT_DIMENSION, 'playerSix');

    //TODO: Code to add each player to teamA or teamB, use the JSON




    //enable click input for characters
    characters.setAll('inputEnabled', true);
    //when a character is clicked, changeStatScreen is called
    //TODO: have changeStatScreen detect which sprite was clicked
    characters.callAll('events.onInputDown.add', 'events.onInputDown', 
        changeStatScreen);


    //log success
    console.log("create() complete");
}

//called every frame, roughly 60 frames per second
function update () {


    //Uncomment this if you want to move one step at a time with a mouse click
    game.input.onTap.add(moveCharactersQuadrant, this);

    //Uncomment this if you want to move the characters by pushing the up arrow
    if(game.input.keyboard.isDown(Phaser.Keyboard.UP)){
        //moveCharacters();
        moveCharactersQuadrant();
    }

}

//DEBUG ONLY WORKS IF RENDERER IS SET TO Phaser.CANVAS
//If you delete this function (it is not needed for the game to work)
//  then you must remove the 'render' key/value from the core game
//  object's constructor
// function render(){
//     console.log("playerOne is at x: " + playerOne.x + ", y: ", playerOne.y);
//     console.log("playerTwo is at x: " + playerTwo.x + ", y", playerTwo.y);
//     console.log("playerThree is at x: " + playerThree.x + ", y", playerThree.y);
// }



//TODO: Delete this dummy JSON for final release
//dummy JSON data for moveCharacters()
//Format:
//
//  characterName--The name of the character you want to update
//      x--The number of MOVEMENT_PIXELS to move in the x-direction
//      y--The number of MOVEMENT_PIXELS to move in the y-direction
//
var locationUpdate = {
    "playerOne" : 
    {
        "x" : 1, 
        "y" : -1
    },
    "playerTwo" : 
    {
        "x" : 0, 
        "y" : 3
    },
    "playerThree" : 
    {
        "x" : 0,
        "y" : -1
    },
    "playerFour" : 
    {
        "x" : 1,
        "y" : 1
    },
    "playerFive" : 
    {
        "x" : -1,
        "y" : 0
    },
    "playerSix" : 
    {
        "x" : 1,
        "y" : 0
    }
};

/**
    Move characters by multiples of MOVEMENT_PIXELS
    Sprites may overlap
    Will probably be deprecated in favor of 
      moveCharactersQuadrant()
*/
function moveCharacters(){
     for (var k in locationUpdate){
        //switch statement to know which character to update
        // by updating the corresponding sprite variable's x and 
        // y fields.
        //The characters move in multiples of MOVEMENT_PIXELS
        switch(k){
            case "playerOne":
                playerOne.x += locationUpdate[k]["x"] * MOVEMENT_PIXELS;
                playerOne.y += locationUpdate[k]["y"] * MOVEMENT_PIXELS;
                break;
            case "playerTwo":
                playerTwo.x += locationUpdate[k]["x"] * MOVEMENT_PIXELS;
                playerTwo.y += locationUpdate[k]["y"] * MOVEMENT_PIXELS;
                break;
            case "playerThree":
                playerThree.x += locationUpdate[k]["x"] * MOVEMENT_PIXELS;
                playerThree.y += locationUpdate[k]["y"] * MOVEMENT_PIXELS;
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
    addSpell(playerThree, playerTwo, "spell1");
    addSpell(playerTwo, playerOne, "spell1");
    addSpell(playerOne, playerThree, "spell1");
    releaseSpells();
}

//List to keep track of caster and target of spells
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



//Represents the map wih a 5x5 array of "tuples"
//Each "tuple" is (row,column) that is available for
//  the next sprite to be inserted
//Access this array in the following way:
//  nextQuadrantSpaceAvailable[quadrantRow][quadrantColumn][0 or 1]
//  0 denotes a row within the quadrant
//  1 denotes a column within the quadrant
var nextQuadrantSpaceAvailable = [
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],
    [[0,0],[0,0],[0,0],[0,0],[0,0] ],

];

//A constant to set nextQuadrantSpaceAvailable to in order
//  to reset it (if using a loop is too expensive)
//TODO: Delete if not necessary
var RESET_QUADRANT_SPACE_AVAILABLE = [
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
      visible. (Have them be in rows)

    Each quadrant is defined to be 120x120 pixels

    Does not check to see if the move is valid
        (does the sprite move off the stage, into a pillar)
*/
function moveCharactersQuadrant(){
    //TODO: Use absolute position if JSON from server gives that

    //reset nextQuadrantSpaceAvailable so every space is "available"
    for(var i = 0; i < 5; i++){
        for(var j = 0; j < 5; j++){
            for(var k = 0; k < 2; k++)
                nextQuadrantSpaceAvailable[i][j][k] = 0;
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
                //move them into the quadrant
                playerOne.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
                playerOne.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
                //move them again to the next column if they're isn't room in the quadrant
                playerOne.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerOne.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] == 3){
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
                console.log("Player2");
                console.log("newQuadrantCol" + newQuadrantCol);
                console.log("newQuadrantRow" + newQuadrantRow);
                playerTwo.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
                playerTwo.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
                //update the column part of the "tuple"
                nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
                //if the column is 3, move to the next row
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] == 3){
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
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] == 3){
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
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] == 3){
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
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] == 3){
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
                if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] == 3){
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
                    nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
                }
                break;
            default:
                break;
        }
        console.log(nextQuadrantSpaceAvailable);
        console.log("newQuadrantCol" + newQuadrantCol);
        console.log("newQuadrantRow" + newQuadrantRow);
    }














    //old movement by quadrant system, did not see if space was "available"

    // for(var k in dummyMovement){
    //     switch(k){
    //         case "playerOne":
    //             playerOne.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
    //             playerOne.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
    //             break;
    //         case "playerTwo":
    //             playerTwo.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
    //             playerTwo.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
    //             break;
    //         case "playerThree":
    //             playerThree.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
    //             playerThree.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
    //             break;
    //         case "playerFour":
    //             playerFour.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
    //             playerFour.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
    //             break;
    //         case "playerFive":
    //             playerFive.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
    //             playerFive.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
    //             break;
    //         case "playerSix":
    //             playerSix.x += dummyMovement[k]["x"] * QUADRANT_DIMENSION;
    //             playerSix.y += dummyMovement[k]["y"] * QUADRANT_DIMENSION;
    //             break;
    //         default:
    //             break;
    //     }
    // }

}






//TODO: Have this display the stats of each sprite on the
//  side bar
function changeStatScreen(){
    console.log("changeStatScreen called");
}



