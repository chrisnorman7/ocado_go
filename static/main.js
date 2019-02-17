function loadSearchResults(e) {
    let response = e.target.response
    let data = JSON.parse(response)
    clearElement(output)
    if (data.error !== undefined) {
        searchResults.innerText = "Error"
        output.innerText = `Error: ${data.error}`
    } else {
        searchResults.innerText = searchString
        for (let per in data) {
            let h3 = document.createElement("h3")
            h3.innerText = per
            output.appendChild(h3)
            for (let product of data[per]) {
                let h4 = document.createElement("h4")
                let a = document.createElement("a")
                a.innerText = `${product.name} ${product.weight}`
                a.target = "_new"
                a.href = product.url
                h4.appendChild(a)
                output.appendChild(h4)
                let p = document.createElement("p")
                p.innerHTML = `${pound}${product.price.toFixed(2)} (${pound}${product.per.toFixed(2)} ${per})`
                output.appendChild(p)
            }
        }
        string.value = ""
    }
    searchButton.disabled = false
    searchButton.value = "Search"
}

function clearElement(e) {
    // Below code based on the first answer at:
    // https://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
    while (e.firstChild) {
        e.removeChild(e.firstChild)
    }
}

let searchString = null
const pound = "&pound;"
const searchResults = document.getElementById("searchResults")
const string = document.getElementById("string")
const searchForm = document.getElementById("searchForm")
const searchButton = document.getElementById("searchButton")
const output = document.getElementById("output")

searchForm.onsubmit = (e) => {
    e.preventDefault()
    searchString = string.value
    if (!searchString) {
        searchString = null
        return alert("You must search for something.")
    }
    searchButton.disabled = true
    searchButton.value = "Loading..."
    output.innerText = "Loading results, please wait."
    let xhr = new XMLHttpRequest()
    xhr.onload = loadSearchResults
    xhr.onerror = () => {
        searchButton.disabled = false
        searchButton.value = "Search"
        output.innerText = "Failed to load search results."
    }
    xhr.open("POST", "/ocado/")
    let fd = new FormData()
    fd.append("string", searchString)
    xhr.send(fd)
}
