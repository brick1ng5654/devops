outputELement = document.querySelector("#helloMessage");
btnELement = document.querySelector(".btnForClick");
inputNameElement = document.querySelector("#name");
inputLastnameElement = document.querySelector("#lastname");

btnELement.addEventListener("click", function () {
    let result = "Здравствуйте, ";
    result = result + inputNameElement.value + " ";
    result = result + inputLastnameElement.value + "!";
    outputELement.innerHTML = result;
});
