async function typeSentence(sentence, eleRef, delay = 100) {
  const letters = sentence.split("");
  let i = 0;
  while(i < letters.length) {
    await waitForMs(delay);
    document.querySelector(eleRef).textContent += letters[i];
    i++
  }
  return;
}


function waitForMs(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function deleteSentence(eleRef) {
  const sentence = document.querySelector(eleRef).textContent;
  const letters = sentence.split("");
  let i = 0;
  while(letters.length > 0) {
    await waitForMs(100);
    letters.pop();
    document.querySelector(eleRef).textContent = letters.join("");
  }
}

const carouselText = ["Welcome, Book Explorer!",
                      "Shhh... Welcome Back to the Library!",
                      "Unlock Imagination: Welcome Back!",
                      "Dive into Words: Welcome, Bibliophile!"];

document.addEventListener("DOMContentLoaded", async function() {
    var i = 0;
    while(true) {
      await typeSentence(carouselText[i], "#sentence");
      await waitForMs(1500);
      await deleteSentence("#sentence");
      await waitForMs(500);
      i++
      if(i >= carouselText.length) {i = 0;}
    }
});