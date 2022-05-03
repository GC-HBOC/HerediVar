class external_link extends HTMLElement {
    constructor() {
      super();
    }
    connectedCallback() {
        var url = this.getAttribute('href');
        var text = this.textContent
        this.innerHTML = `
        <a class="external_link" href=` + url + `>
            ` + text + `<nobr> <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="currentColor" class="bi bi-box-arrow-up-right" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                <path fill-rule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
            </svg></nobr>
        </a>
        `;
      }
  }

class variant_google_link extends HTMLElement {
    constructor(){
        super();
    }
    connectedCallback(){
        //example link: https://www.google.com/search?q=NOC2L+AND+(%221528A%3EC%22+OR+%221528A-%3EC%22+OR+%221528A--%3EC%22+OR+%221528A/C%22+OR+%22Asn510His%22+OR+%22rs72631890%22)
        const is_scholar = this.getAttribute("scholar")
        if (is_scholar === false || is_scholar === null) {
            var link = "https://www.google.com/search?q="
        } else {
            var link = "https://scholar.google.de/scholar?q="
        }
        

        const gene_name = this.getAttribute("gene")
        if (gene_name !== "None"){
            link += gene_name + "+AND+"
        }

        link += "("

        var stuff_for_braces = []

        var cdot = this.getAttribute("hgvs-c")
        var dotpos = cdot.indexOf(".")
        if (dotpos >= 0) {
            const cdotcrop = cdot.substring(dotpos+1)
            stuff_for_braces.push("%22" + cdotcrop.replace('>', '%3E') +"%22")
            stuff_for_braces.push("%22" + cdotcrop.replace('>', '-%3E') + "%22")
            stuff_for_braces.push("%22" + cdotcrop.replace('>', '--%3E') + "%22")
            stuff_for_braces.push("%22" + cdotcrop.replace('>', '/') + "%22")
        }
        

        var pdot = this.getAttribute("hgvs-p")
        dotpos = pdot.indexOf(".")
        if (dotpos >= 0) {
            pdot = pdot.substring(dotpos+1)
            const three_to_one = get_amino_acids()
            var re = new RegExp( Object.keys(three_to_one).join("|"), "ig");
            var one_letter_pdot = pdot.replace(re, function(x) {
                return three_to_one[x.toLowerCase()];
            });
            stuff_for_braces.push("%22" + pdot +"%22")
            stuff_for_braces.push("%22" + one_letter_pdot + "%22")
        }

        var rsid = this.getAttribute("rsid")
        if (rsid !== "None") {
            stuff_for_braces.push("%22" + rsid + "%22")
        }

        link += stuff_for_braces.join('+OR+')
        link += ")"

        this.innerHTML = `
            <external-link href="` + link + `">` + this.textContent +`</external-link>
        `
    }
}
  
customElements.define('external-link', external_link);
customElements.define('variant-google-link', variant_google_link)
