function loadSearchResults() {
    searchButton.disabled = false
    searchButton.value = "Search"
    let html = frame.contentDocument || frame.contentWindow
    if (html.document) html = html.document
    output.innerText = "Works."
}

const frame = document.getElementById("frame")
const baseUrl = "https://www.ocado.com/search?entry="
const string = document.getElementById("string")
const searchForm = document.getElementById("searchForm")
const searchButton = document.getElementById("searchButton")
const output = document.getElementById("output")

window.onload = () => {
    frame.hidden = true
    frame.onload = loadSearchResults
}

searchForm.onsubmit = (e) => {
    e.preventDefault()
    let value = escape(string.value)
    if (!value) {
        return alert("You must search for something.")
    }
    let url = baseUrl + value
    searchButton.disabled = true
    searchButton.value = "Loading..."
    output.innerText = "Loading results, please wait."
    frame.src = url
}
