const string = document.getElementById("string")
const search = document.getElementById("search")

search.onsubmit = (e) => {
    e.preventDefault()
    let value = string.value
    alert(value)
}
