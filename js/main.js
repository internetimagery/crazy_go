import { h, render, Component } from "preact";
import GoBoard from "@sabaki/go-board";
import { Goban } from "@sabaki/shudan";
import html2canvas from "html2canvas";

import "@sabaki/shudan/css/goban.css";
import "../style/main.css";


function toInt(character) {
    return character.charCodeAt()-97;
}

function toChar(number) {
    return String.fromCharCode(number+97);
}

function createTwoWayCheckBox(component) {
  return ({ stateKey, text }) =>
    h(
      "label",
      {
        style: {
          display: "flex",
          alignItems: "center",
        },
      },

      h("input", {
        style: { marginRight: ".5em" },
        type: "checkbox",
        checked: component.state[stateKey],

        onClick: () =>
          component.setState((s) => ({ [stateKey]: !s[stateKey] })),
      }),

      h("span", { style: { userSelect: "none" } }, text)
    );
}

class App extends Component {
  constructor(props) {
    super(props);

    var boardSize = 9;
    var maxPlayers = 2;
    var gamemode = 1;
    var hash = window.location.hash.substring(1);
    if (hash) {
	boardSize = toInt(hash[0]);
	gamemode = toInt(hash[1]) >= 10 ? 1 : 0;
	var maxPlayers = toInt(hash[1]) - (gamemode ? 10 : 0);
    } else {
	window.location.hash = "#" + toChar(boardSize) + toChar(maxPlayers + (gamemode ? 10 : 0));
    }

    this.state = {
      board: GoBoard.fromDimensions(boardSize),
      boardSize,
      vertexSize: 24,
      showCoordinates: false,
      fuzzyStonePlacement: true,
      animateStonePlacement: true,
      isBusy: false,
      players: maxPlayers,
      gamemode,
    };

    this.CheckBox = createTwoWayCheckBox(this);

    for (let [i, move] of (hash.substring(2).match(/[\-a-z]{3}/g) || []).entries()) {
	let player = toInt(move[0]) - 10;
	if (move != "--") {
		let vtx = [toInt(move[1]), toInt(move[2])];
		let {note, newBoard, captures} = this.move(this.state.board, player+1, vtx, gamemode);
		this.setState({ board: newBoard });
	}
    }
  }

  getNeighbors(board, vertex) {
    var neighbours = board.getNeighbors(vertex);

    if (this.state.gamemode) {
      // Normal game mode
      return neighbours;
    }

    // Borderless game mode. Neighbors cross the boundary between sides.
	if (vertex[0] == 0) {
	  neighbours.push([board.width-1, vertex[1]]);
	}
	if (vertex[1] == 0) {
	  neighbours.push([vertex[0], board.height-1]);
	}
	if (vertex[0] == board.width-1) {
	  neighbours.push([0, vertex[1]]);
	}
	if (vertex[1] == board.height-1) {
	  neighbours.push([vertex[0], 0]);
	}

      return neighbours;
  }

  getChain(board, vertex, player) {
	var chain = [];
	var value = board.get(vertex);
	if (!value) {
  	  return chain;
	}

	const isPlayer = value === player;
	var seen = new Set();
	var queue = [vertex];
	while (queue.length) {
	  let vtx = queue.pop();
	  let id = vtx.toString();
	  if (seen.has(id)) {
	    continue;
	  }
          seen.add(id);

	  let val = board.get(vtx);
	  if (!val) {
	    continue;
	  }

	  // If isPlayer then we want only colours of that player.
          // Else we want any other colour that is not that player.
	  if ( (isPlayer && val !== player) || (!isPlayer && val === player) ) {
		  continue;
	  }
	  chain.push(vtx);
          for (let neighbour of this.getNeighbors(board, vtx)) {
	    queue.push(neighbour);
	  }
	}

	return chain;
  }

  move(board, sign, vertex) {
    var newBoard = board;
    var captures = 0;
    var note = "";

    if (sign && board.get(vertex)) {
	note = "Illegal move: stone exists";
	return {note, newBoard, captures}
    }

    if (!sign) {
	newBoard = board.set(vertex, 0);
	return {note, newBoard, captures};
    }

    newBoard = newBoard.set(vertex, sign);

    var toRemove = [];
    var playLiberties = 0;
    for (let neighbour of this.getNeighbors(newBoard, vertex)) {
	let value = newBoard.get(neighbour);
	if (!value || value === sign) {
	    playLiberties ++;
	    continue;
	}
        let chain = this.getChain(newBoard, neighbour, sign);
	let liberties = 0;
	for (let vtx of chain) {
	    for (let space of this.getNeighbors(newBoard, vtx)) {
		if (!board.get(space)) {
		   liberties ++;
		}
	    }
	}
	if (!liberties) {
	    for (let vtx of chain) {
		toRemove.push(vtx);
	    }
	}
    }

    if (!toRemove.length && !playLiberties) {
	note = "Illegal move: self capture";
	newBoard = newBoard.set(vertex, 0);
	return {note, newBoard, captures}
    }


    // Capture
    for (let vtx of toRemove) {
      newBoard = newBoard.set(vtx, 0);
      captures ++;
    }
    return {note, newBoard, captures};
  }

  render() {
    let {
      vertexSize,
      showCoordinates,
      fuzzyStonePlacement,
      animateStonePlacement,
      players,
      boardSize,
      gamemode,
    } = this.state;

    let hash = window.location.hash;
    if (hash.length < 4) {
	window.location.hash = "#" + toChar(boardSize) + toChar(players + (gamemode ? 10 : 0));
	if (boardSize != this.state.board.width) {
            this.setState({ board: GoBoard.fromDimensions(boardSize) });
	}
    }

    return h(
      "section",
      {
        style: {
          display: "grid",
          gridTemplateColumns: "15em auto",
          gridColumnGap: "1em",
        },
      },

      h(
        "form",
        {
          style: {
            display: "flex",
            flexDirection: "column",
          },
        },

        h(
          "p",
          { style: { margin: "0 0 .5em 0" } },
          "Zoom: ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({
                  vertexSize: Math.max(s.vertexSize - 4, 4),
                }));
              },
            },
            "-"
          ),
          " ",

          h(
            "button",
            {
              type: "button",
              title: "Reset",
              onClick: (evt) => {
                this.setState({ vertexSize: 24 });
              },
            },
            "•"
          ),
          " ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({ vertexSize: s.vertexSize + 4 }));
              },
            },
            "+"
          )
        ),

        h(
          "p",
          { style: { margin: "0 0 .5em 0" } },
          "Players: ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({
                  players: Math.max(s.players - 1, 2),
                }));
              },
            },
            "-"
          ),
          " ",

          h(
            "button",
            {
              type: "button",
              title: "Reset",
              onClick: (evt) => {
                this.setState((s) => ({
		  players: toInt(window.location.hash[2]),
		}));
              },
            },
	    players,
          ),
          " ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({ players: Math.min(s.players + 1, 6), }));
              },
            },
            "+"
          )
        ),
        h(
          "p",
          { style: { margin: "0 0 .5em 0" } },
          "Board Size: ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({
                  boardSize: Math.max(s.boardSize - 1, 4),
                }));
              },
            },
            "-"
          ),
          " ",

          h(
            "button",
            {
              type: "button",
              title: "Reset",
              onClick: (evt) => {
                this.setState((s) => ({
		  boardSize: toInt(window.location.hash[1]),
		}));
              },
            },
	    boardSize,
          ),
          " ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({ boardSize: Math.min(s.boardSize + 1, 19), }));
              },
            },
            "+"
          )
        ),

        h(
          "p",
          { style: { margin: "0 0 .5em 0" } },
          "Game Mode: ",

          h(
            "button",
            {
              type: "button",
              onClick: (evt) => {
                this.setState((s) => ({
		    gamemode: s.gamemode ? 0 : 1,
                }));
              },
            },
            gamemode ? "Normal" : "Borderless",
          ),
          " ",
        ),

        h(this.CheckBox, {
          stateKey: "showCoordinates",
          text: "Show coordinates",
        }),
        h(
          "button",
          {
            type: "button",
            onClick: (evt) => {
              var goban = document.getElementsByClassName("shudan-goban")[0];
              html2canvas(goban, {
                  windowWidth: 500,
                  windowHeight: 500,
              }).then(canvas => {
                  let move = window.location.hash.substring(1);
		  console.log(`<img src="${canvas.toDataURL()}"><hr><code>${move}</code>`);

                  const blob = new Blob(
                      [`<img src="${canvas.toDataURL()}"><hr><code>${move}</code>`],
                      {type:"text/html"}
                  );
                  navigator.clipboard.write([
                      new ClipboardItem({
                          "text/html": blob
                      })
                  ]).then( () => {alert("Copied");});
              });
            },
          },
              "Copy Move",
        ),
      ),

      h(
        "div",
        {},
        h(Goban, {
          innerProps: {
            onContextMenu: (evt) => evt.preventDefault(),
          },

	  vertexSize,
          animate: true,

          signMap: this.state.board.signMap,
          showCoordinates,
          fuzzyStonePlacement:true,
          animateStonePlacement:true,

          onVertexMouseUp: (evt, vertex) => {
	    if (evt.button !== 0) {
		return;
	    }
	    let players = toInt(window.location.hash[2]);
	    let gamemode = players >= 10 ? 1 : 0;
	    let moves = window.location.hash.substring(3);
	    let player = moves.length ? toInt(moves[moves.length - 3]) - 10 : -1;

	    player ++;
	    if (player >= this.state.players) {
	        player = 0;
	    }
            let {note, newBoard, captures} = this.move(this.state.board, player+1, vertex, gamemode);
	    if (note) {
		alert(note);
		return;
	    }
	    if (captures) {
	        console.log(captures);
	    }
            this.setState({ board: newBoard });
	    window.location.hash += toChar(player+10) + toChar(vertex[0]) + toChar(vertex[1]);
          },
        }),
      )
    );
  }
}

render(h(App), document.getElementById("root"));

/// ADDITIONAL THINGS

//function loadGameUrl() {
//    var game = decodeURIComponent(location.hash);
//    if (game) {
//        sabaki.loadContent(game.substring(1), "sgf", {suppressAskForSave: true})
//        .then( () => { sabaki.goToEnd() });
//    }
//}
//sabaki.events.on("ready", loadGameUrl);
//addEventListener("hashchange", loadGameUrl);

//function copyMove() {
//    var goban = document.getElementsByClassName("shudan-goban")[0];
//    html2canvas(goban, {
//        windowWidth: 500,
//        windowHeight: 500,
//    }).then(canvas => {
//        let move = window.location.hash.substring(1);
//
//        const blob = new Blob(
//            [`<img src="${canvas.toDataURL()}"><hr><code>${move}</code>`],
//            {type:"text/html"}
//        );
//        navigator.clipboard.write([
//            new ClipboardItem({
//                "text/html": blob
//            })
//        ]).then( () => {alert("Copied");});
//    });
//};
