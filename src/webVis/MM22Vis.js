"use strict";
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
    For this MechMania, the visualizer is updated every TIME_TO_NEXT_UPDATE milliseconds:
        this is done by adding all of the functions that update the visualizer to Phaser's
        internal clock and having the functions be called after TIME_TO_NEXT_UPDATE 
        milliseconds have elapsed

    The core game loop goes as follows (looping call to processTurn):
      As long as there are turns in serverJSON (an array containing turns sent from the server)
        Dequeue the turn
        Move the character sprites on the screen
        Add all spells using addSpell, then call releaseSpell to release them all
        Update the statscreen (update healthbars/attribute strings, move characters)
      

    The server will send a lot of JSON, but it will be added
     to a queue and the front element will be dequeued every
     time the turn is displayed onto the screen, as determined by
     TIME_TO_NEXT_UPDATE.

    
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
*/

//----------Constants and Global Variables------------//
var WEBSOCKET_SERVER_FQDN = "ws://localhost:8080/"
//Reference to the Phaser game
var game;


function WebSocketTest()
         {
            if ("WebSocket" in window)
            {
               //alert("WebSocket is supported by your Browser!");
               
               // Let us open a web socket
               var ws = new WebSocket(WEBSOCKET_SERVER_FQDN);
                
               ws.onopen = function()
               {
                  // Web Socket is connected, send data using send()
                  ws.send("Message to send");
                  //alert("Message is sent...");
               };
                
               ws.onmessage = function (evt) 
               { 
                  console.log(evt);  
                  var received_msg = evt.data;

                  var reader = new FileReader();
                  reader.addEventListener("loadend", function(){
                      var arrayOfTurns = JSON.parse(reader.result).data;
                      arrayOfTurns.forEach(function(data){
                        serverJSON.push(data);
                      });
                      //Instatiate the game
                      //If you want to use game.debug in the render() function, you need to set
                      //  Phaser.AUTO to Phaser.CANVAS (the renderer)
                      //The width is 1000 pixels (GAME_WIDTH + STATWIDTH) and the height is 
                      //  600 pixels (GAME_HEIGHT)
                      game = new Phaser.Game(GAME_WIDTH + STAT_WIDTH, GAME_HEIGHT, Phaser.AUTO,
                       'phaser-game', { preload: preload, create: create, update: update});
                  });
                  
                  //alert("Message is received...");
                  reader.readAsText(received_msg);
               };
                
               ws.onclose = function()
               { 
                  // websocket is closed.
                  alert("Connection is closed..."); 
               };
            }
            
            else
            {
               // The browser doesn't support WebSocket
               alert("Game NOT supported by your Browser!");
            }
         }
WebSocketTest();
//Queue containing all the JSON from the server
var serverJSON = [];


//Number of milliseconds until the next bit of JSON will be processed
//  and the visualizer is updated
var TIME_TO_NEXT_UPDATE = 1000;

//Number of milliseconds allowed for each spell to be tweened
//  i.e. to move from caster to target 
var TIME_FOR_SPELLS = TIME_TO_NEXT_UPDATE/2;

//Number of milliseconds for the whole attack tween chain
var TIME_FOR_ATTACKS = TIME_FOR_SPELLS - (TIME_TO_NEXT_UPDATE/10);



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




//Reference to the game's timer
var timer;

//Pass processTurnTimerEvent to game.time.events.remove()
var processTurnTimerEvent;



// These Graphics Objects are used to draw Health Bars (drawRect)
// Graphics Object for Single Player Stat Screen
var singleGraphics;
// Graphics Object for MultiPlayer Stat Screen
var multiGraphics;


//Width and height of a character's sprite, in pixels
var CHARACTER_DIMENSION = 40;

//Used to add distance in px in the x and y direction if we set 
//  the anchor of character sprites to 0.5
//If we have anchor be its default (top-left corner), set this to 0
var ANCHOR_OFFSET = CHARACTER_DIMENSION/2;

//width and height of a quadrant, in pixels
//The each quadrant is accessed by multiplying QUADRANT_DIMENSION  
//  by 0, 1, 2, 3, or 4
var QUADRANT_DIMENSION = 120;





//Group containing all of the characters we want to use
var characters;

//Arrays that hold the players on each team
var teamA = [];
var teamB = [];


//Mapping of characterID's to 
//  corresponding index within statScreen.MultiPlayer
var characterIDToMultiPlayerIndex = {};




//Core Game Object to contain all of the handles to Phaser text objects 
//  and other things relevant to the stats screen
var statScreen = {
    //If true, display all the character's stats
    //If false, only display the stats of "CharacterName"
    "ShowAll" : false,
    "SinglePlayer" : {
        //Holds the string of the character's name that is being tracked
        "CharacterNameString" : null,
        //Handle to the Text Object containing the tracked character's name
        "CharacterName" : null,
        //Handles to the Phaser.Text Objects of each attribute
        //Use this object if we are tracking only one characer
        "AttributeStrings" : {
            "Damage" : null,
            "SpellPower" : null,
            "Armor" : null,
            "MovementSpeed" : null,
            "Rooted": null,
            "Silenced": null,
            "Stunned": null
        },
        //Contains handles to the rectangle and Text object representing
        //  The health bar
        "HealthBar" : {
            "Bar" : null,
            "HealthText" : null,
            "HEALTH_BAR_X" : GAME_WIDTH + 10,
        },
        //Contains the index of the currently tracked player's position
        //  within the statScreen.MultiPlayer array
        //Defaults to 0 (Player One)
        "PlayerIndex" : 0,
    },
    //Contains All the players, in order
    "MultiPlayer" : [
        { 
            //used in controlling depth of sprites
            "PhaserGroup": null,
            "Sprite" : null,
            //Handle to the Text Object containing the tracked character's name
            "CharacterName" : null,
            //ID of the character according to the game
            "CharacterID": null,
            //Handles to the Phaser.Text Objects of each attribute
            //Use this object if we are tracking only one characer
            "AttributeStrings" : {
                "Damage" : null,
                "SpellPower" : null,
                "Armor" : null,
                "MovementSpeed" : null,
                "Rooted" : null,
                "Silenced" : null,
                "Stunned" : null
            },
            //Contains initial value for each stat
            //Used for coloring each abbreviation correctly
            "InitialValue" : {
                "Damage" : -1,
                "SpellPower" : -1,
                "Armor" : -1,
                "MovementSpeed" : -1,
                "Health" : 500,
                "Rooted" : 0,
                "Silenced" : 0,
                "Stunned" : 0
             },
            //Handle to the Rect Object indicating the player's health
            "HealthBar" : null,
        },
        {
            //used in controlling depth of sprites
            "PhaserGroup": null,
            "Sprite" : null,
            //Handle to the Text Object containing the tracked character's name
            "CharacterName" : null,
            //ID of the character according to the game
            "CharacterID": null,
            //Handles to the Phaser.Text Objects of each attribute
            //Use this object if we are tracking only one characer
            "AttributeStrings" : {
                "Damage" : null,
                "SpellPower" : null,
                "Armor" : null,
                "MovementSpeed" : null,
                "Rooted" : null,
                "Silenced": null,
                "Stunned": null
            },
            "InitialValue" : {
                "Damage" : -1,
                "SpellPower" : -1,
                "Armor" : -1,
                "MovementSpeed" : -1,
                "Health" : 500,
                "Rooted" : 0,
                "Silenced" : 0,
                "Stunned" : 0
             },
            "HealthBar" : null
        },
        {
            //used in controlling depth of sprites
            "PhaserGroup": null,
            "Sprite" : null,
            //Handle to the Text Object containing the tracked character's name
            "CharacterName" : null,
            //ID of the character according to the game
            "CharacterID": null,
            //Handles to the Phaser.Text Objects of each attribute
            //Use this object if we are tracking only one characer
            "AttributeStrings" : {
                "Damage" : null,
                "SpellPower" : null,
                "Armor" : null,
                "MovementSpeed" : null,
                "Rooted" : null,
                "Silenced": null,
                "Stunned": null
            },
            "InitialValue" : {
                "Damage" : -1,
                "SpellPower" : -1,
                "Armor" : -1,
                "MovementSpeed" : -1,
                "Health" : 500,
                "Rooted" : 0,
                "Silenced" : 0,
                "Stunned" : 0
             },
            "HealthBar" : null
        },
        {
            //used in controlling depth of sprites
            "PhaserGroup": null,
            "Sprite" : null,
            //Handle to the Text Object containing the tracked character's name
            "CharacterName" : null,
            //ID of the character according to the game
            "CharacterID": null,
            //Handles to the Phaser.Text Objects of each attribute
            //Use this object if we are tracking only one characer
            "AttributeStrings" : {
                "Damage" : null,
                "SpellPower" : null,
                "Armor" : null,
                "MovementSpeed" : null,
                "Rooted" : null,
                "Silenced": null,
                "Stunned": null
            },
            "InitialValue" : {
                "Damage" : -1,
                "SpellPower" : -1,
                "Armor" : -1,
                "MovementSpeed" : -1,
                "Health" : 500,
                "Rooted" : 0,
                "Silenced" : 0,
                "Stunned" : 0
             },
            "HealthBar" : null
        },
        {
            //used in controlling depth of sprites
            "PhaserGroup": null,
            "Sprite" : null,
            //Handle to the Text Object containing the tracked character's name
            "CharacterName" : null,
            //ID of the character according to the game
            "CharacterID": null,
            //Handles to the Phaser.Text Objects of each attribute
            //Use this object if we are tracking only one characer
            "AttributeStrings" : {
                "Damage" : null,
                "SpellPower" : null,
                "Armor" : null,
                "MovementSpeed" : null,
                "Rooted" : null,
                "Silenced": null,
                "Stunned": null
            },
            "InitialValue" : {
                "Damage" : -1,
                "SpellPower" : -1,
                "Armor" : -1,
                "MovementSpeed" : -1,
                "Health" : 500,
                "Rooted" : 0,
                "Silenced" : 0,
                "Stunned" : 0
             },
            "HealthBar" : null
        },
        {
            //used in controlling depth of sprites
            "PhaserGroup": null,
            "Sprite" : null,
            //Handle to the Text Object containing the tracked character's name
            "CharacterName" : null,
            //ID of the character according to the game
            "CharacterID": null,
            //Handles to the Phaser.Text Objects of each attribute
            //Use this object if we are tracking only one characer
            "AttributeStrings" : {
                "Damage" : null,
                "SpellPower" : null,
                "Armor" : null,
                "MovementSpeed" : null,
                "Rooted" : null,
                "Silenced": null,
                "Stunned": null
            },
            "InitialValue" : {
                "Damage" : -1,
                "SpellPower" : -1,
                "Armor" : -1,
                "MovementSpeed" : -1,
                "Health" : 500,
                "Rooted" : 0,
                "Silenced" : 0,
                "Stunned" : 0
             },
            "HealthBar" : null
        },
    ],
    //reference to the current turn being processed
    "CurrentTurn" : null,

};


//constant of Y-position of where the text of attributes will be positioned
//  relative to this coordinate
var ATTRIBUTE_STRINGS_Y = 230;


//Handles to the Text objects that will act like buttons to switch
//  between the single player and multi-player overlay
var multiButton;
var singleButton;


//Color Constants
//Default Color for strings (orange-ish)
var DEF_COLOR = "#ffa366"

//Health Bar Constants
var HEALTH_BAR_COLOR = 0x33CC33;
//maximum width in pixels the Health Bar will be
var HEALTH_BAR_MAX_WIDTH = 360;

//Handle to HTML span to display turn number
var spanTurnNumberElement;

//------------Main Phaser Code---------------//

//load our assets
function preload () {
    //background image
    game.load.image('background', 'assets/Map-update.png');

    //sprites for the characters 
    game.load.image('Wizard1', 'assets/Wizard1.png');
    game.load.image('Wizard2', 'assets/Wizard2.png');
    game.load.image('Archer1', 'assets/Archer1.png');
    game.load.image('Archer2', 'assets/Archer2.png');
    game.load.image('Druid1', 'assets/Druid1.png');
    game.load.image('Druid2', 'assets/Druid2.png');
    game.load.image('Enchanter1', 'assets/Enchanter1.png');
    game.load.image('Enchanter2', 'assets/Enchanter2.png');
    game.load.image('Warrior1', 'assets/Warrior1.png');
    game.load.image('Warrior2', 'assets/Warrior2.png');
    game.load.image('Sorcerer1', 'assets/Sorcerer1.png');
    game.load.image('Sorcerer2', 'assets/Sorcerer2.png');
    game.load.image('Paladin1', 'assets/Paladin1.png');
    game.load.image('Paladin2', 'assets/Paladin2.png');
    game.load.image('Assassin1', 'assets/Assassin1.png');
    game.load.image('Assassin2', 'assets/Assassin2.png');



    //Spell assets
    game.load.image('spell0', 'assets/Burst.png');
    game.load.image('spell1', 'assets/Stun.png');
    game.load.image('spell2', 'assets/RangeArmorDebuff.png');
    game.load.image('spell3', 'assets/RangeHeal.png');
    game.load.image('spell4', 'assets/RangeArmorBuff.png');
    game.load.image('spell5', 'assets/Silence.png');
    game.load.image('spell6', 'assets/RangeAttackDebuffCurse.png');
    game.load.image('spell7', 'assets/RangeAttackBuff.png');
    game.load.image('spell8', 'assets/SacrificeHealth.png');
    game.load.image('spell9', 'assets/DeepFreeze.png');
    game.load.image('spell10', 'assets/Frostbolt.png');
    game.load.image('spell11', 'assets/Backstab.png');
    //"Sprint"
    game.load.image('spell12', 'assets/SpeedBuff.png');
    game.load.image('spell13', 'assets/Root.png');
    game.load.image('spell14', 'assets/Stun.png');
    game.load.image('spell15', 'assets/ArmorBuff.png');
    game.load.image('spell16', 'assets/Corruption.png');


    
    //log success
    console.log("preload() complete");
}

/**
    Add the assets to the game and make them visible
    Initate any functions to be called on a looping schedule
*/
function create () {

    //Remove the first turn from the array (init information)
    var initInformation = serverJSON[0];
    serverJSON.shift();

    //set background image
    var background = game.add.sprite(0, 0, 'background');

    //create group for characters
    characters = game.add.group();

    //contains all the character objects in the initialInformation
    // as one array to make iteration easier
    var characterArray = [];
    initInformation.forEach(function(teamObject){
        teamObject.Characters.forEach(function(characterInfo){
            characterArray.push(characterInfo);
        });
    });

    //Add all players to the characters group at their initial locations and other init work
    for(var index = 0; index < statScreen.MultiPlayer.length; index++){
      //set CharacterID
      var characterID = characterArray[index].Id;
      statScreen.MultiPlayer[index].CharacterID = characterID;
      characterIDToMultiPlayerIndex[characterID] = index;

      var initPos = calcXAndY(characterArray[index].Position[0], characterArray[index].Position[1]);
     
      //generate the string of the key for the character sprite 
      var teamNumber;
      if(index < 3){
        teamNumber = 1;
      }
      else{
        teamNumber = 2
      }
      //Wizard1.png, Druid2.png etc.
      var spriteName = characterArray[index].ClassId + teamNumber;

      //Add the character's sprite to its own Phaser Group
      //Used for rendering order of sprites
      var characterGroup = game.add.group(); 
      statScreen.MultiPlayer[index].Sprite = characterGroup.create(initPos.x, initPos.y, spriteName);
      statScreen.MultiPlayer[index].PhaserGroup = characterGroup;

      //add the sprite to the characters group (global group)
      characters.add(statScreen.MultiPlayer[index].Sprite);


      //set the anchor of each character sprite to the middle of the sprite
      statScreen.MultiPlayer[index].Sprite.anchor.setTo(0.5);
      statScreen.MultiPlayer[index].Sprite.index = index;
      statScreen.MultiPlayer[index].Sprite.name = characterArray[index].Name;

      //Set initial values of attributes
      for(var attr in statScreen.MultiPlayer[index].InitialValue){
        statScreen.MultiPlayer[index].InitialValue[attr] = 
          characterArray[index].Attributes[attr];
      }
      
    }

    //move the characters so they fit into the regions correctly
    moveCharactersQuadrantAbsolute(serverJSON[0]);


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
    //This function will only update the screen if serverJSON has 
    //  data within it (we aren't waiting for the server to send JSON over)
    processTurnTimerEvent = game.time.events.loop(TIME_TO_NEXT_UPDATE, processTurn, this);

    //add Graphics Object to the Game (used for drawing primitive shapes--health bars)
    singleGraphics = game.add.graphics();
    multiGraphics = game.add.graphics();

    //initializes both SinglePlayer and MultiPlayer screens, but keeps the MultiPlayer 
    //  screen active
    //default to player one
    initSinglePlayerStatScreen(statScreen["MultiPlayer"][0].Sprite);
    statScreen.SinglePlayer.PlayerIndex = 0;
    hideSinglePlayerStatScreen();
    initMultiPlayerStatScreen();

    multiButton = game.add.text(GAME_WIDTH+250, 550, "MULTI", {font: "4em Arial", fill: "#ff944d"});
    multiButton.inputEnabled = true;
    multiButton.events.onInputDown.add(showMultiPlayerStatScreen, this);

    singleButton = game.add.text(GAME_WIDTH+20, 550, "SINGLE", {font: "4em Arial", fill: "#ff944d"});
    singleButton.inputEnabled = true;
    singleButton.events.onInputDown.add(showSinglePlayerStatScreen, this);

    //set up handle on spanTurnNumberElement
    spanTurnNumberElement = document.getElementById("turnNumber");
    

    console.log(serverJSON);

    //log success
    console.log("create() complete");
}

//called every frame, roughly 60 frames per second
//this is unnecessary for MM22
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


//-------------END OF MAIN PHASER CODE-------------------//

















//--------------CODE FOR ACTIONS/SPELLS-------------------//



//List to keep track of caster and target of spells
var spellList = [];


/*
    Adds spell to spellList
    Call releaseSpells() to move all the spell sprites
        to their respective targets.
    If you want a spell to target the caster (self-heal, 
        self-buff), just set caster and target to the
        same value.

    caster--the sprite of the character casting the spell
    casterIndex -- index of the caster within statScreen.MultiPlayer 
    target--the sprite of the charcter targetted by the spell
    spellName--string of the key denoting the sprite of a 
        certain spell.
*/
function addSpell(caster, casterIndex, target, spellName){
    //add spell to center of sprite
    var newSpell = game.add.sprite(caster.x, caster.y, spellName);
    newSpell.anchor.setTo(0.5);

    //add the caster and target to the spellList array
    spellList.push(
      {
        "caster" : caster, 
        "casterIndex": casterIndex,
        "target" : target, 
        "spell" : newSpell
       }
     );
    statScreen.MultiPlayer[casterIndex].PhaserGroup.add(newSpell);
    statScreen.MultiPlayer[casterIndex].PhaserGroup.bringToTop(newSpell);
}

/*
    Releases all the spells that were added by addSpell(),
    moving each spell sprite to their respective target.
    The spell first remains at the sprite of the caster
      (so people can see who is casting the spell),
      then it travels to it's target.
    This function clears spellList.
*/
function releaseSpells(){
  if(spellList.length > 0){
    //Go through all the spells in the spells group
    //  and tween them to their targets
    var holdOnCaster;
    var moveToTarget;
    for(var index = 0; index < spellList.length; index++){
        //get the child, starting at the end of the group
        //  and moving towards the first element
        var currentSpell = spellList[index].spell;
        //moves the spell on the screen, takes TIME_FOR_SPELLS amount of milliseconds
        holdOnCaster = game.add.tween(currentSpell).to({
            x: spellList[index].caster.x, 
            y: spellList[index].caster.y
          }, 
          TIME_FOR_SPELLS/2, null);
        moveToTarget = game.add.tween(currentSpell).to({
            x: spellList[index].target.x, 
            y: spellList[index].target.y
          }, 
          TIME_FOR_SPELLS/2, null);
        holdOnCaster.chain(moveToTarget);
        holdOnCaster.start();

        
   }
    
    //remove spell sprites from caster's group
    //  after the last spell has finished tweening
    moveToTarget.onComplete.add(function(){

      spellList.forEach(function(val){
          var groupIndex = val.casterIndex;
          statScreen.MultiPlayer[groupIndex].PhaserGroup
           .removeChild(val.spell);
      }); 

      //cleanup
      spellList = [];

    }, this);

  }
    
}







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
    Uses assignment from the JSON rather than a +=, so use this if
    the JSON gives ABSOLUTE position rather than relative displacement
*/
function moveCharactersQuadrantAbsolute(currTurn){

   //reset nextQuadrantSpaceAvailable so all spaces are available
    for(var i = 0; i < nextQuadrantSpaceAvailable.length; i++){
        for(var j = 0; j < nextQuadrantSpaceAvailable[i].length; j++){
            nextQuadrantSpaceAvailable[i][j][0] = 0;
            nextQuadrantSpaceAvailable[i][j][1] = 0;
        } 
    }
   
    //contains the positions(x,y) of players in an array as an object
    var playerPositionArray = [];
    var characterArray = convertTurnToPlayerArray(currTurn);
    characterArray.forEach(function(playerObject, index){
        //only move them if they're not dead
        if(playerObject.Attributes.Health > 0){
          playerPositionArray.push({
            x: playerObject.Position[0],
            y: playerObject.Position[1],
            id: playerObject.Id
          });
        }
        //the player is dead, remove their sprite
        else{
          var statScreenIndex = characterIDToMultiPlayerIndex[playerObject.Id];
          statScreen.MultiPlayer[statScreenIndex].Sprite.kill();
        }
    });
    
    for(var index = 0; index < playerPositionArray.length; index++){
        //marks the coordinates of where the player will be after moving
        var newQuadrantRow = 0;
        var newQuadrantCol = 0;

        newQuadrantCol = playerPositionArray[index].x;
        newQuadrantRow = playerPositionArray[index].y;
        var newPosition = calcXAndY(newQuadrantCol, newQuadrantRow);

        var statScreenIndex = characterIDToMultiPlayerIndex[playerPositionArray[index].id];
        //move them into the quadrant at the top-left corner
        statScreen["MultiPlayer"][statScreenIndex].Sprite.x = newPosition.x;
        statScreen["MultiPlayer"][statScreenIndex].Sprite.y = newPosition.y;
        //move them again to the next column if they're isn't room in the quadrant
        statScreen["MultiPlayer"][statScreenIndex].Sprite.x += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] * CHARACTER_DIMENSION;
        statScreen["MultiPlayer"][statScreenIndex].Sprite.y += nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] * CHARACTER_DIMENSION;
        //update the column part of the "tuple"
        nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1]+= 1;
        //if the column is 3, move to the next row
        if(nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] === 3){
            nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][1] = 0;
            nextQuadrantSpaceAvailable[newQuadrantRow][newQuadrantCol][0] += 1;
        }
    }

}















//-----------------Code for Stats Screen---------------------//

/**
    The Stats Screen has two states:
        1) Single Player--Shows the numerical stats of one player only
        2) Multiplayer--Shows the net change of each players' stats by
            means of a red or green string for each attribute and a health bar

    To switch between states, the user clicks on the text saying 
        "Single" or "Multi"
    When clicked, each Text Object will kill the other stat screen 
        (clicking "Single" while the Multiplayer screen is up will
        mean that the Multiplayer screen is killed and all of its 
        associated objects are no longer visible) and revive the 
        stat screen associated with its stat screen.
        The killing and reviving are done via the kill/revive functions
        for the SinglePlayer and MultiPlayer screens.

*/

/**
    Draws the SinglePlayer Stat Screen and tracks the character's stats
    This should be called only once as it actually creates Text Objects.
    If you want to redraw the single player stats screen after killing it,
        call showSinglePlayerStatScreen()

    character--The variable referring to the Sprite of the character
        (defaults to player one)
*/
function initSinglePlayerStatScreen(character){
    var HEALTH_BAR_X = GAME_WIDTH + 10;
    var HEALTH_BAR_Y = 100;
    var HEALTH_BAR_HEIGHT = 20;
    console.log("initSinglePlayerScreen");
    statScreen.ShowAll = false;
    //set the Text displaying which character we are tracking
    statScreen.SinglePlayer.CharacterNameString = character.name;
    statScreen.SinglePlayer.CharacterName = game.add.text(GAME_WIDTH + 10, 10, character.name.toUpperCase(), {font: "4em Arial", fill: "#ff944d"});

    singleGraphics.clear();
    //redraw the healthbar and the text saying 'Health'
    singleGraphics.beginFill(HEALTH_BAR_COLOR);
    statScreen.SinglePlayer.HealthBar.Bar = singleGraphics.drawRect(HEALTH_BAR_X, HEALTH_BAR_Y, 
        HEALTH_BAR_MAX_WIDTH, 
        HEALTH_BAR_HEIGHT);
    singleGraphics.endFill();
    statScreen.SinglePlayer.HealthBar.HealthText = game.add.text(GAME_WIDTH + (STAT_WIDTH/2) -30, 
        HEALTH_BAR_Y + HEALTH_BAR_HEIGHT + 10, "Health", {fill: "#33cc33", font: "2em Arial"});


    //Constant used to specify how many pixels to space out each attribute in the y-direction
    var attrStrSpacing = 35;
    //add the Attribute Strings to the StatScreen
    statScreen.SinglePlayer.AttributeStrings.MovementSpeed = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y, 
        "Movement Speed: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.MovementSpeed, 
        {font: "3em Arial", fill: DEF_COLOR});
    statScreen.SinglePlayer.AttributeStrings.Damage = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y + attrStrSpacing, 
        "Damage: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.Damage, 
        {font: "3em Arial", fill: DEF_COLOR});
    statScreen.SinglePlayer.AttributeStrings.SpellPower = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y + 2*attrStrSpacing, 
        "Spell Power: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.SpellPower, 
        {font: "3em Arial", fill: DEF_COLOR});
    statScreen.SinglePlayer.AttributeStrings.Armor = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y + 3*attrStrSpacing,
        "Armor: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.Armor, 
        {font: "3em Arial", fill: DEF_COLOR});
    statScreen.SinglePlayer.AttributeStrings.Rooted = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y + 4*attrStrSpacing,
        "Rooted: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.Rooted, 
        {font: "3em Arial", fill: DEF_COLOR});
    statScreen.SinglePlayer.AttributeStrings.Stunned = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y + 5*attrStrSpacing,
        "Stunned: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.Stunned, 
        {font: "3em Arial", fill: DEF_COLOR});
    statScreen.SinglePlayer.AttributeStrings.Silenced = game.add.text(GAME_WIDTH + 20, 
        ATTRIBUTE_STRINGS_Y + 6*attrStrSpacing,
        "Silenced: " + statScreen.MultiPlayer[statScreen.SinglePlayer.PlayerIndex].InitialValue.Silenced, 
        {font: "3em Arial", fill: DEF_COLOR});

}

/**
    Creates The Text Objects for the multiplayer stat screen.
    Like initSinglePlayerScreen, this method should be called only once 
*/
function initMultiPlayerStatScreen(){
    console.log("initMultiPlayerStatScreen");

    var attrstyle = {font: "2em Arial", fill: DEF_COLOR};
    var nameStyle = {font: "3em Arial", fill: DEF_COLOR};
    //The height of each player's health bar
    var MULTI_HEALTHBAR_HEIGHT = 10;

    //defines where to start drawing text objects
    var startX = GAME_WIDTH + 20;

    //clear any graphics that were on the screen
    multiGraphics.clear();
    //Have it so all health bars have the same "fill" (color)
    multiGraphics.beginFill(HEALTH_BAR_COLOR);

    //Start drawing at y-coordinate of 5
    var yPos = 5;
    //Y-coordinate of where to draw the attribute strings
    var attrStrY = 0;
    //Draw the player stats
    for(var player in statScreen.MultiPlayer){

      //init character name
      statScreen.MultiPlayer[player].CharacterName = game.add.text(startX, yPos, 
          statScreen.MultiPlayer[player].Sprite.name.toUpperCase(), nameStyle);

      attrStrY = statScreen.MultiPlayer[player].CharacterName.y + 
        statScreen.MultiPlayer[player].CharacterName.height - 5;
  
      //Create all the Text Objects for each player
      //init attribute strings
      //handle to the Attribute Strings...saves on typing
      var strings = statScreen.MultiPlayer[player].AttributeStrings;
      strings.Damage = game.add.text(startX, 
        attrStrY, "DMG", attrstyle);
      strings.SpellPower = game.add.text(strings.Damage.x 
          + strings.Damage.width + 5,
          attrStrY, "SP", attrstyle);
      strings.Armor = game.add.text(strings.SpellPower.x 
          + strings.SpellPower.width + 5, 
          attrStrY, "ARMOR", attrstyle);
      strings.MovementSpeed = game.add.text(strings.Armor.x 
          + strings.Armor.width + 5, 
          attrStrY, "MS", attrstyle);
      strings.Rooted = game.add.text(strings.MovementSpeed.x 
          + strings.MovementSpeed.width + 5, 
          attrStrY, "RT", attrstyle);
      strings.Stunned = game.add.text(strings.Rooted.x 
          + strings.Rooted.width + 5, 
          attrStrY, "STUN", attrstyle);
      strings.Silenced = game.add.text(strings.Stunned.x 
          + strings.Stunned.width + 5, 
          attrStrY, "SIL", attrstyle);
  
      //draw the healthbar
      statScreen.MultiPlayer[player].HealthBar = multiGraphics.drawRect(startX, 
          strings.MovementSpeed.y + strings.MovementSpeed.height, 
          HEALTH_BAR_MAX_WIDTH, 
          MULTI_HEALTHBAR_HEIGHT);

      //update yPos
      yPos += strings.MovementSpeed.height + MULTI_HEALTHBAR_HEIGHT + 50;
  
  }

    multiGraphics.endFill();

}

/**
    Revives the Multiplayer screen by calling hideSinglePlayerStatScreen()
        and then calling revive() on all the text objects associated with
        the multiplayer screen
    This must be called after initMultiPlayerStatScreen has been called
*/
function showMultiPlayerStatScreen(){
  //only change if we're at the single player screen now
  if(!statScreen.ShowAll){
    console.log("showMultiPlayerStatScreen");
    hideSinglePlayerStatScreen();
    for (var player in statScreen.MultiPlayer){
            statScreen.MultiPlayer[player]["CharacterName"].revive();
            for (var attrString in statScreen.MultiPlayer[player]["AttributeStrings"]){
                if(statScreen.MultiPlayer[player]["AttributeStrings"].hasOwnProperty(attrString)){
                    statScreen.MultiPlayer[player]["AttributeStrings"][attrString].revive();
                }
            }
    }
    
    //redraw all the healthBars
    multiGraphics.beginFill(HEALTH_BAR_COLOR);
    var startX = GAME_WIDTH + 20;
    var MULTI_HEALTHBAR_HEIGHT = 10;
    var strings;
    for(player in statScreen.MultiPlayer){
      strings = statScreen.MultiPlayer[player].AttributeStrings;
      statScreen.MultiPlayer[player].HealthBar = multiGraphics.drawRect(startX, 
        strings.MovementSpeed.y + strings.MovementSpeed.height, 
        calcHealthBarWidth(statScreen.CurrentTurn, player), 
        MULTI_HEALTHBAR_HEIGHT);

    }

    multiGraphics.endFill();
  }

}

/**
    Helper function that calls kill() on all the Text Objects associated with the
        multiplayer stat screen
*/
function hideMultiPlayerStatScreen(){
    console.log("hideMultiPlayerStatScreen");
    //clear all the healthbars
    multiGraphics.clear();
    //Call kill on all Phaser Text Objects of all players
    for (var player in statScreen.MultiPlayer){
        if(statScreen.MultiPlayer.hasOwnProperty(player)){
            statScreen.MultiPlayer[player]["CharacterName"].kill();
            for (var attrString in statScreen.MultiPlayer[player]["AttributeStrings"]){
                if(statScreen.MultiPlayer[player]["AttributeStrings"].hasOwnProperty(attrString)){
                    statScreen.MultiPlayer[player]["AttributeStrings"][attrString].kill();
                }
            }
        }

    }
}

/*
    Kills all of the single player stat screen's objects from being seen
    This does not destroy the object, but makes it invisible.
    To show the single player stat screen again, call showSinglePlayerStatScreen
*/
function hideSinglePlayerStatScreen(){
    console.log("hideSinglePlayerStatScreen")
    //indicate we are showing all of the player's stats
    statScreen.ShowAll = true;
    //Clears the healthbar
    singleGraphics.clear();
    statScreen.SinglePlayer.HealthBar.HealthText.kill();
    //kill all the Text objects for the singlePlayer screen
    for (var k in statScreen.SinglePlayer.AttributeStrings){
        if(statScreen.SinglePlayer.AttributeStrings.hasOwnProperty(k)){
            statScreen.SinglePlayer.AttributeStrings[k].kill();
        }
    }
    //kill the Text object containing the player name
    statScreen.SinglePlayer.CharacterName.kill();

}


/**
    Revives (redraws) the single player screen
    This must be called after initSinglePlayerScreen() has been called
    This method does not create new Text Objects, but rather "revives" the Text objects
        by calling Phaser's revive() method on them
*/
function showSinglePlayerStatScreen(){
  //only run if we're on the multiplayer screen
  if(statScreen.ShowAll){
    console.log("reviveSinglePlayerStatScreen");
    hideMultiPlayerStatScreen();
    statScreen.ShowAll = false;
    statScreen.SinglePlayer.CharacterName.revive();

    var HEALTH_BAR_X = GAME_WIDTH + 10;
    var HEALTH_BAR_Y = 100;
    var HEALTH_BAR_HEIGHT = 20;

    singleGraphics.clear();
    //redraw the healthbar and the text saying 'Health'
    singleGraphics.beginFill(HEALTH_BAR_COLOR);
    statScreen.SinglePlayer.HealthBar.Bar = singleGraphics.drawRect(HEALTH_BAR_X, HEALTH_BAR_Y, 
        calcHealthBarWidth(statScreen.CurrentTurn, statScreen.SinglePlayer.PlayerIndex), 
        HEALTH_BAR_HEIGHT);
    singleGraphics.endFill();

    statScreen.SinglePlayer.HealthBar.HealthText.revive();


    //Revive all the Attribute Strings
    for (var attrStr in statScreen.SinglePlayer.AttributeStrings){
        if(statScreen.SinglePlayer.AttributeStrings.hasOwnProperty(attrStr)){
            statScreen.SinglePlayer.AttributeStrings[attrStr].revive();
        }
    }
    
  }

    
}

/**
    This core game-loop function is run every TIME_TO_NEXT_UPDATE milliseconds
    Moves characters according to game JSON
    Casts spells and visualizes attacks
    Updates both MultiPlayer and SinglePlayer stat screens 
      (although only one is visible at any time)
    
*/
var turnNum = 0;
function processTurn(){
  if(serverJSON.length > 0){

    console.log("Turn Number : " + turnNum);
    turnNumber.innerHTML = "Turn Number: " + turnNum;
    turnNum++;

    
    //dequeue
    var currTurn = serverJSON.shift();
    //console.log(currTurn);
    statScreen.CurrentTurn = currTurn;
    //move the sprites
    moveCharactersQuadrantAbsolute(currTurn);

    //resolves everything in turnResults (attacks/spells)
    resolveActions(currTurn);

    //update both stat screens (although only one will be showing)
    //  at any time
    updateMultiPlayerStatScreen(currTurn);
    updateSinglePlayerStatScreen(currTurn);
  }
}

/**

  Animates any actions occuring in turnResults  

  */
function resolveActions(currTurn){
  //constant determined by Python Game to signify a successful action
  var ACTION_SUCCESSFUL = "Ok";

  var teamATweens = [];
  var teamBTweens = [];

  for(var i = 0; i < currTurn.TurnResults.length; i++){
    currTurn.TurnResults[i].forEach(function(action){
      if(action.Status == ACTION_SUCCESSFUL){
        var actionType = action.Action;
        //the id of the character making the action
        var casterID = action.CharacterId;
        var casterMultiPlayerIndex = characterIDToMultiPlayerIndex[casterID];
        var casterSprite = statScreen.MultiPlayer[casterMultiPlayerIndex].Sprite;
        //the id of the character targetted by the action
        var targetID = action.TargetId;
        var targetMultiPlayerIndex = characterIDToMultiPlayerIndex[targetID];
        switch(actionType){
          case "Attack":
            var targetSprite = statScreen.MultiPlayer[targetMultiPlayerIndex].Sprite;
            //do attack stuff
            var attackTween = game.add.tween(casterSprite).to(
                {
                  x: targetSprite.x,
                  y: targetSprite.y
                },
                TIME_FOR_ATTACKS/4,
                null,
                false,
                0,
                0,
                true
            );
            //It's an attack from team A
            if(i == 0){
              teamATweens.push(attackTween);
            }
            //Attack from team B
            else{
              teamBTweens.push(attackTween);
            }
            break;
          case "Move":
            //do nothing since movement is handled by another function
            break;
          case "Cast":
            var targetSprite = statScreen.MultiPlayer[targetMultiPlayerIndex].Sprite;
            //the spell was successfully cast, so call addSpell and 
            //  pass in corresponding arguments
            var casterIndex = characterIDToMultiPlayerIndex[action.CharacterId];
            var casterSrite = statScreen.MultiPlayer[casterIndex].Sprite;
            var targetIndex = characterIDToMultiPlayerIndex[action.TargetId];
            var targetSprite = statScreen.MultiPlayer[targetIndex].Sprite;
            var spellName = "spell" + action.AbilityId;

            addSpell(casterSprite, casterIndex, targetSprite, spellName);
            break;
        }
      }
      
  });

  } //end for loop for turnResults

  //have any tweens for teamB after all (or none) of
  // team A's tweens have completed
  if(teamATweens.length > 0){
    teamATweens[teamATweens.length-1].onComplete.add(function(){
      teamBTweens.forEach(function(tween){
          tween.start();
      });
    }
    , this);
    teamATweens.forEach(function(tween){
        tween.start();
    }); 
  }
  //team A had no turns, so just do team B's tweens
  else{
    teamBTweens.forEach(function(tween){
        tween.start();
    }); 
  }

  //release all spells
  releaseSpells();
}



/**
    Changes which character's stats are displayed
        in the SinglePlayer screen.
  
  character--the Phaser.Sprite object associated with that
    character
*/
function changeStatScreen(character){
    //update PlayerIndex of statScreen 
    statScreen.SinglePlayer.PlayerIndex = character.index;
    statScreen.SinglePlayer.CharacterNameString = character.name;
    //clear all graphics drawn from the graphics reference
    singleGraphics.clear();
    //updates the name of the character whose stats are displayed
    //NOTE: Does not check to see if name will fit yet
    statScreen.SinglePlayer.CharacterName.setText((character.name).toUpperCase());
    //redraw health bar and update stats if on the single player screen
    if(!statScreen.ShowAll){
      updateSinglePlayerHealthBar(statScreen.CurrentTurn);
      updateSinglePlayerStatScreen(statScreen.CurrentTurn);
    }
}


/**
    Updates the colors of the AtrributeStrings of each player
        green if they have a buff
        red if they have a debuff
        orange if neutral


    Currently this has random data, but once the JSON is finalized
        I can add in the logic

    Parameters:
      currTurn--the turn as given by the server(JSON)

    Warning: This has a hardcoded font size for the AttributeStrings rather than attrStyle
        (didn't want to make that a global variable)
*/
function updateMultiPlayerStatScreen(currTurn){
    console.log("updateMultiPlayerStatScreen");

    //update the color of the strings
    statScreen.MultiPlayer.forEach(function(player, index){
        for (var attrString in player["AttributeStrings"]){
            //ignore AttackRange attribute
            if(player["AttributeStrings"].hasOwnProperty(attrString) && attrString != "AttackRange"){               
                player["AttributeStrings"][attrString].setStyle({
                    font: "2em Arial", 
                    fill: chooseColor(currTurn, index, attrString) 
                });
            }
        }
    }); 

    //update healthbars only if we're on the multiplayer stat screen
    multiGraphics.clear();
    if(statScreen.ShowAll){
      multiGraphics.beginFill(HEALTH_BAR_COLOR);
      var startX = GAME_WIDTH + 20;
      var MULTI_HEALTHBAR_HEIGHT = 10;
      var strings;
      for (var player in statScreen.MultiPlayer){
        strings = statScreen.MultiPlayer[player].AttributeStrings;
        statScreen.MultiPlayer[player].HealthBar = multiGraphics.drawRect(
          startX, 
          strings.MovementSpeed.y + strings.MovementSpeed.height, 
          calcHealthBarWidth(currTurn, player),
          MULTI_HEALTHBAR_HEIGHT);
      }

      multiGraphics.endFill();
    }
}

/**
    Called to update all the graphics associated with the 
        Stats Screen.
    If the character selected has changed, call changeStatScreen() before this

   Parameters:
    --currTurn The next turn that was dequeued from the serverJSON
*/
function updateSinglePlayerStatScreen(currTurn){
  console.log("updateSinglePlayerStatScreen");
  singleGraphics.clear();
  //only redraw the health bar if we're on the single player stat screen
  if(!statScreen.ShowAll){
    updateSinglePlayerHealthBar(currTurn);
  }

    // update each Attribute String with data from the queue, and randomly switch each string to be 
    //  red (#ff0000) or green (#00ff00)
    // in the finished version the green or red will depend on a buff or debuff
   var characterArray = convertTurnToPlayerArray(currTurn); 
    for(var attrStr in statScreen.SinglePlayer.AttributeStrings){
        if(statScreen.SinglePlayer.AttributeStrings.hasOwnProperty(attrStr)){
            //the attribute string with appropiate spacing if necessary
            //"MovementSpeed" --> "Movement Speed"
            var spacedAttrStr = attrStr;
            switch(attrStr){
              case "MovementSpeed":
                spacedAttrStr = "Movement Speed"
                break;
              case "SpellPower":
                spacedAttrStr = "Spell Power"
                break;
              default:
                break;
            }
            statScreen.SinglePlayer.AttributeStrings[attrStr]
              .setText(spacedAttrStr + ": " + characterArray[statScreen.SinglePlayer.PlayerIndex].Attributes[attrStr]);
            statScreen.SinglePlayer.AttributeStrings[attrStr].setStyle({
                font: "3em Arial", 
                fill: chooseColor(currTurn, statScreen.SinglePlayer.PlayerIndex, attrStr),
            });
        }
    }

}


/**
    Redraws the Health Bar for the Single Player StatScreen
    Currently it sets to health bar to a random value,
        but later it will set to the health of the current
        player.

   Parameters:
    --currTurn The next turn that was dequeued from the serverJSON
*/
function updateSinglePlayerHealthBar(currTurn){

    var HEALTH_BAR_X = GAME_WIDTH + 10;
    var HEALTH_BAR_Y = 100;
    var HEALTH_BAR_HEIGHT = 20;
    //Calculate the width of the bar as a percentage of the player's current health
    var healthBarWidth = calcHealthBarWidth(currTurn, statScreen.SinglePlayer.PlayerIndex);
    //redraw the health bar
    singleGraphics.beginFill(HEALTH_BAR_COLOR);
    statScreen.SinglePlayer.HealthBar.Bar = singleGraphics.drawRect(
        HEALTH_BAR_X, 
        HEALTH_BAR_Y, 
        healthBarWidth, 
        HEALTH_BAR_HEIGHT);
    singleGraphics.endFill();
}




//----------------------HELPER FUNCTIONS----------------------//

/**
  Returns the width of the Health Bar, adjusted for the 
    player's current health

  Params:
    --currTurn: The current turn given from serverJSON
    --playerNumber: The index of the player in the statScreen.MultiPlayer array
  */
function calcHealthBarWidth(currTurn, playerNumber){
  if(currTurn == null){
    return HEALTH_BAR_MAX_WIDTH;
  }
  var characterArray = convertTurnToPlayerArray(currTurn);
  var currHealth = characterArray[playerNumber].Attributes.Health;
  var maxHealth = statScreen.MultiPlayer[playerNumber].InitialValue.Health;
  var width = Math.floor((currHealth*HEALTH_BAR_MAX_WIDTH)/maxHealth);
  return width;
}

/**
  Returns which color the attribute string should be
    based on the player's current stats.
  Returns RED if the player's current stats are below their
    intial value.
  Returns GREEN if the player's current stats are above their
    intial value.
  Returns DEF_COLOR if the player's current stats are at their
    intial value.

  This function should not be called to handle Health.

  Params:
    --currTurn: The current turn given from serverJSON
    --playerNumber: The index of the player in the statScreen.MultiPlayer array
    --attribute: The attribute of the player we are looking at
*/
function chooseColor(currTurn, playerNumber, attribute){
  var RED = '#ff0000';
  var GREEN = '#00ff00';

  //contains all the character objects in the initialInformation
  // as one array to make iteration easier
  var characterArray = convertTurnToPlayerArray(currTurn);
   
  var currValue = characterArray[playerNumber].Attributes[attribute];
  var initialValue = statScreen.MultiPlayer[playerNumber].InitialValue[attribute];
     
  if(currValue === initialValue){
    return DEF_COLOR;
  }
  else if (currValue < initialValue){
    return RED;
  }
  else if (currValue > initialValue){
    return GREEN;
  }
  //returns white, should never be reached
  else{
    return '#ffffff';
  }
}

/**
  Helper function that returns x and y positions of sprites based on which 
    "quadrant" they are in.
  Takes into account anchor offset
  Returns undefined if the row or column is not [0-4]
  */
function calcXAndY(row, column){
  if(row < 0 || row > 4 || column < 0 || column > 4){
    return undefined
  }
  return {
    x: row * QUADRANT_DIMENSION + ANCHOR_OFFSET,
    y: column * QUADRANT_DIMENSION + ANCHOR_OFFSET,
  };
}

/**
  Helper function that takes current Turn and converts it 
    to a flat array with only players' stats
  */
function convertTurnToPlayerArray(currTurn){
  var playerArray = [];
  currTurn.Teams.forEach(function(team){
      team.Characters.forEach(function(player){
          playerArray.push(player);
      });
  });
  return playerArray;
}

/**
  Pauses/Resumes game when user clicks the pause/play button
*/
function pauseGame(){
  var pauseButton = document.getElementById("pauseButton");
  //Toggle button text and add/remove processTurn from core game timer as necessary
  switch(pauseButton.value){
    case "Pause":
      pauseButton.value = "Resume"
      game.time.events.removeAll();
      break;
    case "Resume":
      pauseButton.value = "Pause"
      processTurnTimerEvent = game.time.events.loop(TIME_TO_NEXT_UPDATE, processTurn, this);
      break;
    default:
      break;
  } 
}






