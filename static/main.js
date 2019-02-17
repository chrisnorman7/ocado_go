function loadSearchResults(e) {
    let response = e.target.response
    let data = JSON.parse(response)
    clearElement(output)
    if (data.error !== undefined) {
        output.innerText = `Error: ${data.error}`
    } else {
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

const pound = "&pound;"
const string = document.getElementById("string")
const searchForm = document.getElementById("searchForm")
const searchButton = document.getElementById("searchButton")
const output = document.getElementById("output")

searchForm.onsubmit = (e) => {
    e.preventDefault()
    let value = string.value
    if (!value) {
        return alert("You must search for something.")
    }
    searchButton.disabled = true
    searchButton.value = "Loading..."
    output.innerText = "Loading results, please wait."
    let xhr = new XMLHttpRequest()
    xhr.onload = loadSearchResults
    xhr.open("POST", "/ocado/")
    let fd = new FormData()
    fd.append("string", string.value)
    xhr.send(fd)
}
