// Sound mapping using keyCodes
const sound = {
  65: "http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav", // 'A' key
  87: "http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav", // 'W' key
  83: "http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav", // 'S' key
  69: "http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav", // 'E' key
  68: "http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav", // 'D' key
  70: "http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav", // 'F' key
  84: "http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav", // 'T' key
  71: "http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav", // 'G' key
  89: "http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav", // 'Y' key
  72: "http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav", // 'H' key
  85: "http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav", // 'U' key
  74: "http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav", // 'J' key
  75: "http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav", // 'K' key
  79: "http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav", // 'O' key
  76: "http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav", // 'L' key
  80: "http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav", // 'P' key
  186: "http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav" // ';' key
};

function playSound(event) {
  const keyCode = event.keyCode;
  if (sound[keyCode]) {
      const audio = new Audio(sound[keyCode]);
      // Play corresponding audio
      audio.play();
  }
}

document.addEventListener("keydown", playSound);

document.addEventListener("DOMContentLoaded", function() {
  const piano = document.querySelector(".piano");
  const keyLabels = document.querySelectorAll(".key-label");

  // Show key labels on mouseover
  piano.addEventListener("mouseover", function() {
      keyLabels.forEach(label => {
          label.style.opacity = 1; // Reveal the key label
      });
  });

  // Hide key labels on mouseout
  piano.addEventListener("mouseout", function() {
      keyLabels.forEach(label => {
          label.style.opacity = 0; // Hide the key label
      });
  });
});

document.addEventListener("DOMContentLoaded", function() {
  const keyMap = {
      'a': document.querySelector(".white-key:nth-child(1)"),
      's': document.querySelector(".white-key:nth-child(2)"),
      'd': document.querySelector(".white-key:nth-child(3)"),
      'f': document.querySelector(".white-key:nth-child(4)"),
      'g': document.querySelector(".white-key:nth-child(5)"),
      'h': document.querySelector(".white-key:nth-child(6)"),
      'j': document.querySelector(".white-key:nth-child(7)"),
      'k': document.querySelector(".white-key:nth-child(8)"),
      'l': document.querySelector(".white-key:nth-child(9)"),
      ';': document.querySelector(".white-key:nth-child(10)"),
      'w': document.querySelector(".black-key-1"),
      'e': document.querySelector(".black-key-2"),
      't': document.querySelector(".black-key-3"),
      'y': document.querySelector(".black-key-4"),
      'u': document.querySelector(".black-key-5"),
      'o': document.querySelector(".black-key-6"),
      'p': document.querySelector(".black-key-7")
  };

  let keySequence = ""; //track keys
  const targetSequence = "UYTYUUUYYYUOOUYTYUUUUYYUYT";

  document.addEventListener("keydown", function(event) {
      const key = event.key.toLowerCase(); // Capture lowercase key

      if (keyMap[key]) {
          keyMap[key].style.backgroundColor = "lightblue"; //change background
          setTimeout(function() {
              if (keyMap[key].classList.contains("white-key")) {
                  keyMap[key].style.backgroundColor = "white"; // Reset white key color
              } else {
                  keyMap[key].style.backgroundColor = "black"; // Reset black key color
              }
          }, 200);
      }

      // Update sequence
      keySequence += key;

      if (keySequence.includes(targetSequence.toLowerCase())) { // if uytyuuuyyyuoouytyuuuuyyuyt in string
          const lambAudio = new Audio('/static/piano/sounds/lamb.mp3');
        lambAudio.play();

      
          // Fade out the piano
          const piano = document.querySelector(".piano");
          piano.style.opacity = 0;
      
          // Fade in the texture after fading out
          const texture = document.querySelector(".texture");
          texture.style.display = "block";
          setTimeout(() => {
              texture.style.opacity = 1;
          }, 500);
      
          // Remove the keydown event listener for keyMap
          document.removeEventListener("keydown", arguments.callee);
      
          // Remove event listener for audio sound
          document.removeEventListener("keydown", playSound);
      }                
  });
});
