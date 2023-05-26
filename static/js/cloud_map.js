var spaceSpeed = 0;
var loadCount = 0;

function loadingStarted() {
    loadCount++;
}

function loadingFinished() {
    if (loadCount > 0) loadCount--;
}

function isLoading() {
    return loadCount != 0;
}

// Fills cloud div with vpcsData
function fillClouds(cloudsDiv, vpcsData) {
    var cloudsDocumentFragment = document.createDocumentFragment();

    for (const vpc of vpcsData) {
        const vpcDiv = document.createElement("div");
        vpcDiv.classList.add("vpc");
        vpcDiv.dataset.id = vpc.id;

        const headerDiv = document.createElement("div");
        headerDiv.classList.add("vpc-header");

        const headerText1 = document.createElement("p");
        headerText1.innerHTML = `<i class="fa-solid fa-cloud"></i> ${vpc.name}`;

        const headerText2 = document.createElement("p");
        headerText2.textContent = vpc.cidr;

        headerDiv.appendChild(headerText1);
        headerDiv.appendChild(headerText2);

        vpcDiv.appendChild(headerDiv);

        const subnetsDiv = document.createElement("div");
        subnetsDiv.classList.add("vpc-subnets");

        for (const subnet of vpc.subnets) {
            const subnetDiv = document.createElement("div");
            subnetDiv.classList.add("subnet");
            subnetDiv.dataset.id = subnet.id;

            const subnetHeaderDiv = document.createElement("div");
            subnetHeaderDiv.classList.add("subnet-header");

            const subnetHeaderText1 = document.createElement("p");
            subnetHeaderText1.innerHTML = `<i class="fa-solid fa-network-wired"></i> ${subnet.name}`;

            const subnetHeaderText2 = document.createElement("p");
            subnetHeaderText2.textContent = subnet.cidr;

            subnetHeaderDiv.appendChild(subnetHeaderText1);
            subnetHeaderDiv.appendChild(subnetHeaderText2);

            subnetDiv.appendChild(subnetHeaderDiv);

            const vmsDiv = document.createElement("div");
            vmsDiv.classList.add("subnet-vms");

            for (const vm of subnet.vms) {
                const vmDiv = document.createElement("div");
                vmDiv.classList.add("vm");
                vmDiv.dataset.id = vm.id;

                const vmHeaderDiv = document.createElement("div");
                vmHeaderDiv.classList.add("vm-header");

                const vmHeaderText = document.createElement("p");
                vmHeaderText.innerHTML = `${vm.name}`;

                if (vm.publicIP) {
                    vmHeaderText.innerHTML +=
                        ' <i class="fa-solid fa-globe"></i>';
                }

                vmHeaderDiv.appendChild(vmHeaderText);

                const vmInfoDiv = document.createElement("div");
                vmInfoDiv.classList.add("vm-info");

                vmDiv.appendChild(vmHeaderDiv);
                vmDiv.appendChild(vmInfoDiv);

                vmsDiv.appendChild(vmDiv);
            }

            subnetDiv.appendChild(vmsDiv);

            subnetsDiv.appendChild(subnetDiv);
        }

        vpcDiv.appendChild(subnetsDiv);

        cloudsDocumentFragment.appendChild(vpcDiv);
    }

    cloudsDiv.appendChild(cloudsDocumentFragment);
}

// Fills internet div with internet nodes
function fillInternet(internetDiv, internetNodes) {
    var internetDocumentFragment = document.createDocumentFragment();

    for (const address of internetNodes) {
        const networkDiv = document.createElement("div");
        networkDiv.classList.add("network");

        const networkText = document.createElement("p");
        networkDiv.dataset.address = address;
        networkText.innerHTML = `<i class="fa-solid fa-globe"></i> ${address}`;

        networkDiv.appendChild(networkText);

        internetDocumentFragment.appendChild(networkDiv);
    }

    const addDiv = document.createElement("div");
    addDiv.classList.add("network");
    addDiv.id = "add-network";
    const addText = document.createElement("p");
    addText.innerHTML = '<i class="fa-solid fa-add"></i> Add target';
    addDiv.appendChild(addText);
    internetDocumentFragment.appendChild(addDiv);

    // Append the document fragment to the internet div
    internetDiv.appendChild(internetDocumentFragment);
}

function deepEqual(x, y) {
    return x && y && typeof x === "object" && typeof y === "object"
        ? Object.keys(x).length === Object.keys(y).length &&
              Object.keys(x).reduce(function (isEqual, key) {
                  return isEqual && deepEqual(x[key], y[key]);
              }, true)
        : x === y;
}

function getNodeType(element) {
    var exInfo = getNodeTypeEx(element);
    if (!exInfo) return null;
    // truncate info
    delete exInfo.elem;
    return exInfo;
}

function getNodeTypeEx(element) {
    if (!element) return null;
    const interestedElem = element.closest(".vpc,.subnet,.vm,.network");
    if (!interestedElem) return null;

    if (interestedElem.classList.contains("vpc")) {
        return {
            type: "vpc",
            id: interestedElem.dataset.id,
            elem: interestedElem,
        };
    }

    if (interestedElem.classList.contains("subnet")) {
        return {
            type: "subnet",
            id: interestedElem.dataset.id,
            elem: interestedElem,
        };
    }

    if (interestedElem.classList.contains("vm")) {
        return {
            type: "vm",
            id: interestedElem.dataset.id,
            elem: interestedElem,
        };
    }

    if (interestedElem.classList.contains("network")) {
        return {
            type: "network",
            address: interestedElem.dataset.address,
            elem: interestedElem,
        };
    }
}

function getVPCInfo(id) {
    const vpcs = window.data.vpcs;
    for (const vpc of vpcs) {
        if (vpc.id == id) return vpc;
    }
}

function getSubnetInfo(id) {
    const vpcs = window.data.vpcs;
    for (const vpc of vpcs) {
        for (const subnet of vpc.subnets) {
            if (subnet.id == id)
                return {
                    vpc_id: vpc.id,
                    subnet: subnet,
                };
        }
    }
}

function getVMInfo(id) {
    const vpcs = window.data.vpcs;
    for (const vpc of vpcs) {
        for (const subnet of vpc.subnets) {
            for (const vm of subnet.vms) {
                if (vm.id == id)
                    return {
                        vpc_id: vpc.id,
                        subnet_id: subnet.id,
                        vm: vm,
                    };
            }
        }
    }
}

function getSelection() {
    const existingSelected = document.querySelector(".selected");
    if (existingSelected) {
        return getNodeType(existingSelected);
    }
}

// Create security modal protocol changed
function updateSecurityRuleVisibility() {
    const service = document.getElementById("service").value;
    const protocol = document.getElementById("protocol").value;

    const protocolRow = document.getElementById("protocol-row");
    const portRow = document.getElementById("port-row");
    const icmpRow = document.getElementById("icmp-row");

    if (service === "custom") {
        protocolRow.classList.remove("d-none");
        if (protocol === "ICMP") {
            portRow.classList.add("d-none");
            icmpRow.classList.remove("d-none");
        } else {
            portRow.classList.remove("d-none");
            icmpRow.classList.add("d-none");
        }
    } else {
        protocolRow.classList.add("d-none");
        portRow.classList.add("d-none");
        icmpRow.classList.add("d-none");
    }
}

function addOutboundForSourceChanged() {
    const checked = document.querySelector("#addOutboundForSource").checked;
    var elements = document.querySelectorAll(
        "#usePrivateIPdst, #usePublicIPdst"
    );
    if (checked) {
        elements.forEach((el) => {
            el.classList.remove("d-none");
        });
    } else {
        elements.forEach((el) => {
            el.classList.add("d-none");
        });
    }
}

function addInboundForDestinationChanged() {
    const checked = document.querySelector("#addInboundForDestination").checked;
    var elements = document.querySelectorAll(
        "#usePrivateIPsrc, #usePublicIPsrc"
    );
    if (checked) {
        elements.forEach((el) => {
            el.classList.remove("d-none");
        });
    } else {
        elements.forEach((el) => {
            el.classList.add("d-none");
        });
    }
}

function getIPOf(obj) {
    switch (obj.type) {
        case "subnet":
            return getSubnetInfo(obj.id).subnet.cidr;
        case "vpc":
            return getVPCInfo(obj.id).cidr;
        case "network":
            return obj.address;
        default:
            return null;
    }
}

function clearMessagesFrom(element) {
    element.querySelectorAll(".alert").forEach((el) => {
        el.remove();
    });
}

function showMessageTo(element, message) {
    clearMessagesFrom(element);

    // Create the alert element
    let alertEl = document.createElement("div");
    alertEl.classList.add(
        "alert",
        "alert-danger",
        "alert-dismissible",
        "fade",
        "show"
    );
    alertEl.setAttribute("role", "alert");

    // Create the error message element
    let errorMessageEl = document.createElement("span");
    errorMessageEl.setAttribute("id", "errorMessage");
    errorMessageEl.textContent = message;

    // Create the close button element
    let closeButtonEl = document.createElement("button");
    closeButtonEl.classList.add("btn-close");
    closeButtonEl.setAttribute("type", "button");
    closeButtonEl.setAttribute("data-bs-dismiss", "alert");
    closeButtonEl.setAttribute("aria-label", "Close");

    // Add the error message and close button to the alert element
    alertEl.appendChild(errorMessageEl);
    alertEl.appendChild(closeButtonEl);

    // Insert the alert element after the #create-rule-form element
    element.appendChild(alertEl);
}

function securityRuleShowErrorAlert(message) {
    let ruleForm = document.querySelector("#create-rule-form");
    showMessageTo(ruleForm.parentNode, message);
}

function recalculateLinks() {
    // Get the coordinates of the center of a div
    function getCenterCoordinates(element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        return { x: centerX, y: centerY };
    }


    // Calculate the angle between two points in degrees
    function calculateAngle(point1, point2) {
        const deltaX = point2.x - point1.x;
        const deltaY = point2.y - point1.y;
        let radians = Math.atan2(deltaY, deltaX);        
        if (radians < 0) {
            radians += 2 * Math.PI;
        }
        return radians;
    }

    function calculateDistance(point1, point2){
        let y = point1.x - point2.x;
        let x = point1.y - point2.y;
        
        return Math.sqrt(x * x + y * y);
    }
    
    function findIntersection(alpha, width, height) {
        var rayDirX = Math.cos(alpha);
        var rayDirY = Math.sin(alpha);
        
        var x1 = -width / 2, y1 = -height / 2;
        var x2 = width / 2, y2 = height / 2;
        
        var intersection = null;
        
        // top or bottom
        if (rayDirY < 0) {
            intersection = {x: rayDirX / rayDirY * (y1 - 0) + 0, y: y1};
            if (intersection.x >= x1 && intersection.x <= x2) {
                return intersection;
            }
        } else if (rayDirY > 0) {
            intersection = {x: rayDirX / rayDirY * (y2 - 0) + 0, y: y2};
            if (intersection.x >= x1 && intersection.x <= x2) {
                return intersection;
            }
        }
        
        // left or right
        if (rayDirX < 0) {
            intersection = {x: x1, y: rayDirY / rayDirX * (x1 - 0) + 0};
            if (intersection.y >= y1 && intersection.y <= y2) {
                return intersection;
            }
        } else if (rayDirX > 0) {
            intersection = {x: x2, y: rayDirY / rayDirX * (x2 - 0) + 0};
            if (intersection.y >= y1 && intersection.y <= y2) {
                return intersection;
            }
        }

        return null;
    }
    
    function linePointInfo(div, label, angle) {
        let data = {
            "target": div,
            "label": label,            
            "socketGravity": 'auto'
        };
        if (angle) {
            let divClientRect = div.getBoundingClientRect();
            let divPoint = findIntersection(angle, divClientRect.width, divClientRect.height);
            data.target = LeaderLine.pointAnchor(div, {
                x: divPoint.x + divClientRect.width / 2,
                y: divPoint.y + divClientRect.height / 2
            });
            data.socketGravity = [
                Math.cos(angle) * 150, 
                Math.sin(angle) * 150
            ];
        }
        return data;
    }


    let links = window.links;
    if (links && links.length > 0) {
        links.forEach(link => {
            const center1 = getCenterCoordinates(link.info.srcDiv);
            const center2 = getCenterCoordinates(link.info.dstDiv);  
            link.calculated.srcDstAngle = calculateAngle(center1, center2);
            link.calculated.srcDstDist = calculateDistance(center1, center2);
            link.calculated.srcAngle = link.calculated.srcDstAngle;
            link.calculated.dstAngle = null;
            link.calculated.swap = center1.x > center2.x;

            // special cases
            if (link.calculated.srcDstDist < 200) {                
                link.calculated.dstAngle = link.calculated.srcAngle;
                link.calculated.dstAngle += Math.PI / 4;
                link.calculated.srcAngle += Math.PI / 2;
            }
            if (link.data.to.type == "network") {
                link.calculated.dstAngle = 3 * Math.PI / 2;
            }
        });

        
        // sort by angle
        links.sort((a,b) => a.calculated.srcAngle - b.calculated.srcAngle);

        let maxGap = 0.0;
        let maxGapPos = 0.0;
        if (links.length > 1) {
            maxGap = links[0].calculated.srcAngle + (2 * Math.PI - links[links.length - 1].calculated.srcAngle);
            maxGapPos = 0;
            for (let i = 1; i < links.length; i++) {            
                let gap = links[i].calculated.srcAngle - links[i - 1].calculated.srcAngle;
                if (gap > maxGap) {
                    maxGapPos = i;
                    maxGap = gap;  
                }                  
            }
        }
        let newGap = maxGap / 3;
        console.log('maxGap', maxGap, 'newGap', newGap);

        
        let delta = (2 * Math.PI - newGap) / (links.length);
        let start = links[maxGapPos].calculated.srcAngle - newGap / 2;
        if (start < 0) {
            start = start + 2 * Math.PI;
        }

        let i = maxGapPos;
        let iteration = 0;
        do {
            links[i].calculated.srcAngle = (start + delta * iteration);
            if (links[i].calculated.srcAngle > 2 * Math.PI) {
                links[i].calculated.srcAngle -= 2 * Math.PI;
            }
            i = i + 1;
            if (i == links.length) {
                i = 0;
            }
            iteration = iteration + 1;
        }
        while (i != maxGapPos);

        // draw line
        links.forEach(link => {
            // delete old line
            let line = link.line;
            link.line = null;
            if (line) {
                line.remove();
            }

            let linePointInfo1 = linePointInfo(link.info.srcDiv, link.info.srcLabel, link.calculated.srcAngle);
            let linePointInfo2 = linePointInfo(link.info.dstDiv, link.info.dstLabel, link.calculated.dstAngle);            
                        
            if (link.calculated.swap) {
                let tmpPoint = linePointInfo1;
                linePointInfo1 = linePointInfo2;
                linePointInfo2 = tmpPoint;
            }


            // create new line
            line = new LeaderLine(
                linePointInfo1.target,                
                linePointInfo2.target,
                {
                    middleLabel: LeaderLine.pathLabel(
                        (linePointInfo1.label ?? "") + "⟷" + (linePointInfo2.label ?? ""),
                        {
                        color: "#8A2BE2",
                        outlineColor: "#d5b7de"
                        }
                    ),
                    
                    color: "rgba(0, 0, 0, 0.8)",
                    outline: true,
                    outlineColor: "rgba(245, 245, 220, 0.7)",
                    startSocketGravity: linePointInfo1.socketGravity,
                    endSocketGravity: linePointInfo2.socketGravity,
                    endPlug: "behind",
                    path: "fluid"
                });
            link.line = line;
        });
    }
}

async function refreshLinks() {
    // remove old lines
    if (window.links) {
        let links = window.links;
        window.links = null;
        links.forEach((link) => {
            if (link.line) {
                link.line.remove();
            } 
        });
    }

    // clear security rules table
    let tableBody = document.querySelector("#rulesWindow tbody");
    tableBody.innerHTML = "";
    window.securityRules = null;

    // add new lines
    let sel = window.SelectedNode;
    if (sel && sel.type == "vm") {
        const id = sel.id;

        loadingStarted();
        const response = await fetch(`/vm/${id}/links`);
        loadingFinished();
        if (response.status == 200) {
            const data = await response.json();
            console.log('Links for vm with id="', id, '": ', data);

            // Process links

            const srcDiv = sel.elem;

            let links = data.links.map((link) => {
                // find destination item
                let dstDivQuery = "";
                if (link.to.type == "network") {
                    dstDivQuery = `.${link.to.type}[data-address='${link.to.address}']`;
                } else if (link.to.type == "vpc") {
                    dstDivQuery = `.${link.to.type}[data-id='${link.to.id}'] .vpc-subnets`;
                } else if (link.to.type == "subnet") {
                    dstDivQuery = `.${link.to.type}[data-id='${link.to.id}'] .subnet-vms`;
                } else {
                    dstDivQuery = `.${link.to.type}[data-id='${link.to.id}']`;
                }
                dstDiv = document.querySelector(dstDivQuery);

                return {
                    "data": link,
                    "info": {
                        "srcDiv": srcDiv,
                        "srcLabel": link.inbound,
                        "dstDiv": dstDiv,
                        "dstLabel": link.outbound
                    },
                    "calculated": { },
                    "line": null
                };
            });

            console.log(links);
            window.links = links;
            
            recalculateLinks();

            // Process rules

            const securityRules = data.rules;

            securityRules.forEach((rule) => {
                const tr = document.createElement("tr");
                tr.setAttribute("data-id", rule.id);

                const checkboxTd = document.createElement("td");
                const checkboxLabel = document.createElement("label");
                checkboxLabel.className = "form-check-label";
                const checkboxInput = document.createElement("input");
                checkboxInput.type = "checkbox";
                checkboxInput.className = "form-check-input";
                checkboxLabel.appendChild(checkboxInput);
                checkboxTd.appendChild(checkboxLabel);
                tr.appendChild(checkboxTd);

                const groupTd = document.createElement("td");
                groupTd.textContent = rule.group_id;
                tr.appendChild(groupTd);

                const egressTd = document.createElement("td");
                egressTd.textContent = rule.egress;
                tr.appendChild(egressTd);

                const protoTd = document.createElement("td");
                protoTd.textContent = rule.proto;
                tr.appendChild(protoTd);

                const naddrTd = document.createElement("td");
                naddrTd.textContent = rule.naddr;
                tr.appendChild(naddrTd);

                const portsTd = document.createElement("td");
                portsTd.textContent = rule.ports;
                tr.appendChild(portsTd);

                tableBody.appendChild(tr);
            });

            window.securityRules = securityRules;
        } else {
            console.log('Response for vm with id="', id, '": ', response);
            alert("Cannot get links :(");
        }
    }
}

async function createLink() {
    const src = window.createSecurityRuleInfo.src;
    const dst = window.createSecurityRuleInfo.dst;
    console.log("createLink", "src=", src, "dst=", dst);

    var rules = [];
    /*
    {
        "selected": {
            "type": "vm",
            "id": 1 // | 2 | ...
        },
        "type": "inbound", // | "outbound"
        "rule": {
            "ip": "10.0.0.1/32",
            "proto": "TCP", // | "UDP" | "ICMP"
            "port": "10100", // "10000-11000" | "80, 443" | ... for "TCP" | "UDP"
            "icmp_type": "2", // "" for any
            "icmp_code": "3" // "" for any
        }
    }
    */

    let ruleTemplate = {};
    const ruleService = document.querySelector("#service").value;
    const ruleType = document.querySelector("#protocol").value;
    if (ruleService === "custom") {
        if (ruleType == "TCP" || ruleType == "UDP") {
            ruleTemplate = {
                ip: "",
                service: ruleService,
                proto: ruleType,
                port: document.querySelector("#port").value,
            };
        } else if (ruleType == "ICMP") {
            ruleTemplate = {
                ip: "",
                service: ruleService,
                proto: ruleType,
                icmp_type: document.querySelector("#type").value,
                icmp_code: document.querySelector("#code").value,
            };
        } else {
            console.log("unknown type: ", ruleType);
            return;
        }
    } else {
        ruleTemplate = {
            ip: "",
            service: ruleService,
        };
    }

    // add outbound rules
    if (
        src.type == "vm" &&
        document.querySelector("#addOutboundForSource").checked
    ) {
        let dstIPs = [];
        if (dst.type == "vm") {
            let dstvm = getVMInfo(dst.id);
            let checkbox = document.querySelector("#usePrivateIPdst");
            if (checkbox && checkbox.checked && dstvm.vm.privateIP)
                dstIPs.push(dstvm.vm.privateIP);
            checkbox = document.querySelector("#usePublicIPdst");
            if (checkbox && checkbox.checked && dstvm.vm.publicIP)
                dstIPs.push(dstvm.vm.publicIP);
        } else {
            const ip = getIPOf(dst);
            if (ip) dstIPs.push(ip);
        }

        if (dstIPs.length == 0) {
            console.log("no selected IP addresses in Destination");
            securityRuleShowErrorAlert(
                "Please select IP address(es) in Destination"
            );
            return;
        }

        dstIPs.forEach((ip) => {
            const rule = Object.assign({}, ruleTemplate);
            rule.ip = ip;
            rules.push({
                selected: {
                    type: "vm",
                    id: src.id,
                },
                type: "outbound",
                rule: rule,
            });
        });
    }

    // add inbound rules
    if (
        dst.type == "vm" &&
        document.querySelector("#addInboundForDestination").checked
    ) {
        let srcIPs = [];
        if (src.type == "vm") {
            let srcvm = getVMInfo(src.id);
            let checkbox = document.querySelector("#usePrivateIPsrc");
            if (checkbox && checkbox.checked && srcvm.vm.privateIP)
                srcIPs.push(srcvm.vm.privateIP);
            checkbox = document.querySelector("#usePublicIPsrc");
            if (checkbox && checkbox.checked && srcvm.vm.publicIP)
                srcIPs.push(srcvm.vm.publicIP);
        } else {
            const ip = getIPOf(src);
            if (ip) srcIPs.push(ip);
        }

        if (srcIPs.length == 0) {
            console.log("no selected IP addresses in Source");
            securityRuleShowErrorAlert(
                "Please select IP address(es) in Source"
            );
            return;
        }

        srcIPs.forEach((ip) => {
            const rule = Object.assign({}, ruleTemplate);
            rule.ip = ip;
            rules.push({
                selected: {
                    type: "vm",
                    id: dst.id,
                },
                type: "inbound",
                rule: rule,
            });
        });
    }

    if (rules.length == 0) {
        console.log("no rules was generated");
        securityRuleShowErrorAlert(
            "Please choose to create an outbound and/or inbound rule(s)"
        );
        return;
    }

    console.log("/cloudmap/addrule", rules);
    loadingStarted();
    document
        .querySelectorAll("#createSecurityRuleModal button")
        .forEach((el) => {
            el.disabled = true;
        });
    const response = await fetch("/cloudmap/addrule", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(rules),
    });
    document
        .querySelectorAll("#createSecurityRuleModal button")
        .forEach((el) => {
            el.disabled = false;
        });
    loadingFinished();

    if (response.status == 200) {
        window.CreateSecurityRuleModal.hide();
    } else {
        securityRuleShowErrorAlert(await response.text());
    }
    refreshLinks();
}

function selectNode(node) {
    // clear selection
    const existingSelected = document.querySelector(".selected");
    if (existingSelected) {
        existingSelected.classList.remove("selected");
    }

    // selection
    let sel = getNodeTypeEx(node);

    // network cannot be selected
    if (sel && sel.type == "network") sel = null;

    // add "selected" class to selected elem
    if (sel) {
        sel.elem.classList.add("selected");
    }

    // update selection
    window.SelectedNode = sel;

    // refresh links
    refreshLinks();
}

function disableTextSelection(disabled) {
    document.body.style.userSelect = disabled ? "none" : "auto";
    document.body.style.MozUserSelect = disabled ? "none" : "auto";
    document.body.style.msUserSelect = disabled ? "none" : "auto";
}

function addHideButton(elmnt) {
    var contentElement = elmnt.querySelector(".dcontent");
    if (!contentElement) {
        console.log("addHideButton failed: no .dcontent", elmnt);
        return;
    }

    var hideButton = document.createElement("button");
    hideButton.style.float = "left";
    hideButton.style.background = "transparent";
    hideButton.style.border = "none";
    hideButton.style.color = "black";
    hideButton.style.cursor = "pointer";

    hideButton.innerHTML = "&#9776;";

    elmnt.querySelector(".dheader").prepend(hideButton);

    if (contentElement.classList.contains("d-none")) {
        if (!contentElement.getAttribute("data-height")) {
            contentElement.setAttribute(
                "data-height",
                contentElement.style.height
            );
            contentElement.style.height = 0;
        }
        if (!contentElement.getAttribute("data-width")) {
            contentElement.setAttribute(
                "data-width",
                contentElement.style.width
            );
            contentElement.style.width = 0;
        }
    }
    hideButton.addEventListener("mousedown", function (event) {
        event.stopPropagation();
    });
    hideButton.addEventListener("click", function (event) {
        event.stopPropagation();
        contentElement.style.transition =
            "height 0.3s ease-in-out, width 0.3s ease-in-out";
        if (contentElement.classList.contains("d-none")) {
            contentElement.classList.remove("d-none");
            setTimeout(function () {
                contentElement.style.height =
                    contentElement.getAttribute("data-height");
                contentElement.style.width =
                    contentElement.getAttribute("data-width");
            }, 1);
        } else {
            contentElement.setAttribute(
                "data-height",
                contentElement.style.height
            );
            contentElement.setAttribute(
                "data-width",
                contentElement.style.width
            );
            contentElement.style.height = "0";
            contentElement.style.width = "0";
            setTimeout(function () {
                contentElement.classList.add("d-none");
            }, 300);
        }
        setTimeout(function () {
            contentElement.style.transition = "";
        }, 300);
    });
}

function makeMoving(elmnt) {
    var pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();

        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;

        elmnt.style.top = elmnt.offsetTop - pos2 + "px";
        elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
    }

    function closeDragElement() {
        document.removeEventListener("mouseup", closeDragElement);
        document.removeEventListener("mousemove", elementDrag);
    }

    function dragMouseDown(e) {
        if (e.button !== 0) return; // Allow only left mouse button

        e = e || window.event;
        e.preventDefault();

        pos3 = e.clientX;
        pos4 = e.clientY;
        document.addEventListener("mouseup", closeDragElement);
        document.addEventListener("mousemove", elementDrag);
    }

    if (elmnt.querySelector(".dheader")) {
        elmnt
            .querySelector(".dheader")
            .addEventListener("mousedown", dragMouseDown);
    } else {
        elmnt.addEventListener("mousedown", dragMouseDown);
    }
}

function makeResizable(elmnt, minWidth, minHeight) {
    var startX, startY, startWidth, startHeight;
    var sizedElement = elmnt;

    function onMouseMove(e) {
        var newWidth = startWidth + (e.clientX - startX);
        var newHeight = startHeight + (e.clientY - startY);

        if (newWidth >= minWidth) {
            sizedElement.style.width = newWidth + "px";
        }
        if (newHeight >= minHeight) {
            sizedElement.style.height = newHeight + "px";
        }
    }

    function onMouseUp() {
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
        disableTextSelection(false);
    }

    function onMouseDown(e) {
        if (e.button !== 0) return; // Allow only left mouse button

        startX = e.clientX;
        startY = e.clientY;
        startWidth = parseInt(
            document.defaultView.getComputedStyle(sizedElement).width,
            10
        );
        startHeight = parseInt(
            document.defaultView.getComputedStyle(sizedElement).height,
            10
        );
        disableTextSelection(true);
        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
    }

    var resizeHandle = document.createElement("div");
    resizeHandle.classList.add("resize-handler");

    if (sizedElement.querySelector(".dcontent")) {
        sizedElement = sizedElement.querySelector(".dcontent");
    }

    sizedElement.appendChild(resizeHandle);
    resizeHandle.addEventListener("mousedown", onMouseDown);
}

async function rulesDeleteSelected() {
    const selected = window.SelectedNode;
    if (!selected || selected.type !== "vm") {
        console.log('rulesDeleteSelected: !selected || selected.type !== "vm"');
        return;
    }

    let selectedCheckboxes = document.querySelectorAll(
        "#rulesWindow tbody tr td:first-child input[type='checkbox']:checked"
    );
    if (selectedCheckboxes.length == 0) {
        console.log("rulesDeleteSelected: selectedCheckboxes.length == 0");
        return;
    }

    let ids = Array.from(selectedCheckboxes).map((cb) =>
        Number(cb.closest("tr").getAttribute("data-id"))
    );
    let vmId = selected.id;

    loadingStarted();
    const response = await fetch(`/vm/${vmId}/links/delete`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(ids),
    });
    loadingFinished();

    if (response.status != 200) {
        const errorMessage = await response.text();
        console.log("rulesDeleteSelected result: ", errorMessage);
        showMessageTo(
            document.querySelector("#rulesWindow .messages"),
            errorMessage
        );
    }
    await refreshLinks();
}

function init() {
    // Global settings
    LeaderLine.positionByWindowResize = false;
    window.addEventListener('resize', (e) => {
        recalculateLinks();
    });

    // selected
    window.SelectedNode = null;

    // create modals
    window.NetworkAddressModal = new bootstrap.Modal(
        document.getElementById("networkAddressModal")
    );
    window.CreateSecurityRuleModal = new bootstrap.Modal(
        document.getElementById("createSecurityRuleModal")
    );

    // Fill vpcs
    fillClouds(document.querySelector(".clouds"), window.data.vpcs);

    // Fill internet nodes
    fillInternet(
        document.querySelector(".internet"),
        window.data.internetNodes
    );

    // Add vms event listener
    const vms = document.querySelectorAll(".vm");
    vms.forEach((vm) => {
        vm.addEventListener("click", async (event) => {
            event.stopPropagation();

            selectNode(event.currentTarget);
        });
    });

    // Add subnets event listener
    const subnets = document.querySelectorAll(".subnet");
    subnets.forEach((subnet) => {
        subnet.addEventListener("click", async (event) => {
            event.stopPropagation();

            selectNode(event.currentTarget);
        });
    });

    // Add vpcs event listener
    const vpcs = document.querySelectorAll(".vpc");
    vpcs.forEach((vpc) => {
        vpc.addEventListener("click", async (event) => {
            event.stopPropagation();

            selectNode(event.currentTarget);
        });
    });

    // Add networks event listener
    const networks = document.querySelectorAll(".network");
    networks.forEach((network) => {
        network.addEventListener("click", async (event) => {
            event.stopPropagation();

            selectNode(event.currentTarget);

            const selected = event.currentTarget;
            const address = selected.dataset.address;
            if (!address) {
                // add
                window.NetworkAddressModal.show();
            }
        });
    });

    // Clear selection on .content
    document
        .querySelector(".content")
        .addEventListener("click", async (event) => {
            selectNode(event.currentTarget);
        });

    // Dragable
    var dragimg = document.createElement("img");
    dragimg.src =
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAANpJREFUOE+t0zFKA1EQxvFfkBzDe6T2BjYBIZVVWk3lDVKIYpsbqJ0XEDt7+5DCG1gqRGaZhcfuy7oQp1rem/l/38ybnTgyJkfWGwOY47Ei1NSWgHNE8kkmv+MOp5jl2RJn+d0DfOEDnx1AK36NW7wmpAfYp4Pnit2rdHODbbY0GlAWr1MkZjIK0Npe4T6dtTNpnJZD7LYwxRsisS3udTcEiOSAfBdV4SgiXqeJvwBdxac8iOf+f8APHhALdCiihR0uag42uCw2sQaJZVvgpQYYED58NeZnGgT/AkoGLhGxK7BzAAAAAElFTkSuQmCC";

    function generateVMContent(vmInfo, isSource, isVM2VM) {
        var privateIP = vmInfo.privateIP || "No Private IP";
        var publicIP = vmInfo.publicIP || "No Public IP";
        const isSourcePostfix = isSource ? "src" : "dst";

        if (vmInfo.publicIP) {
            publicIP = `${publicIP} <i class=\"fa-solid fa-globe\"></i>`;
        }

        if (isVM2VM) {
            if (vmInfo.privateIP) {
                privateIP = `<input class="form-check-input d-none" type="checkbox" value="" id="usePrivateIP${isSourcePostfix}">
                            <label class="form-check-label" for="usePrivateIP${isSourcePostfix}">
                                ${privateIP}
                            </label>`;
            }
            if (vmInfo.publicIP) {
                publicIP = `<input class="form-check-input d-none" type="checkbox" value="" id="usePublicIP${isSourcePostfix}">
                            <label class="form-check-label" for="usePublicIP${isSourcePostfix}">
                                ${publicIP}
                            </label>`;
            }
        }

        return `
            <div class="vm" data-id="${vmInfo.id}">
            <div class="vm-header">
                <p>${vmInfo.name}</p>
            </div>
            <div class="vm-info">
                <p>${privateIP}</p>
                <p>${publicIP}</p>
            </div>
            </div>`;
    }

    function generateSubnetContent(subnetInfo) {
        return `
            <div class="subnet" data-id="${subnetInfo.id}">
            <div class="subnet-header">
                <p><i class="fa-solid fa-network-wired"></i> ${subnetInfo.name}</p>
                <p>${subnetInfo.cidr}</p>
            </div>
            <div class="subnet-vms"></div>
            </div>`;
    }

    function generateVPCContent(vpcInfo) {
        return `
            <div class="vpc" data-id="${vpcInfo.id}">
            <div class="vpc-header">
                <p><i class="fa-solid fa-cloud"></i> ${vpcInfo.name}</p>
                <p>${vpcInfo.cidr}</p>
            </div>
            <div class="vpc-subnets">
            </div>
            </div>`;
    }

    function generateNetworkContent(networkInfo) {
        return `
            <div class="network" data-address="${networkInfo.address}">
            <div class="network-header">
                <p><i class="fa-solid fa-globe"></i> ${networkInfo.address}</p>
            </div>
            </div>`;
    }

    function getContentByType(data, isSource, isVM2VM) {
        switch (data.type) {
            case "vm":
                return generateVMContent(
                    getVMInfo(data.id).vm,
                    isSource,
                    isVM2VM
                );
            case "subnet":
                return generateSubnetContent(getSubnetInfo(data.id).subnet);
            case "vpc":
                return generateVPCContent(getVPCInfo(data.id));
            case "network":
                return generateNetworkContent(data);
            default:
                return "";
        }
    }

    function updateSourceAndDestinationContent(src, dst) {
        const sourceContent = document.getElementById("source-content");
        const destinationContent = document.getElementById(
            "destination-content"
        );
        const isVM2VM = src.type == "vm" && dst.type == "vm";

        sourceContent.innerHTML = getContentByType(src, true, isVM2VM);
        destinationContent.innerHTML = getContentByType(dst, false, isVM2VM);
    }

    function prepareCreateLink(src, dst) {
        updateSourceAndDestinationContent(src, dst);

        // checkboxes manipulation
        const isSrcVM = src.type == "vm";
        const isDstVM = dst.type == "vm";
        const isVM2VM = isSrcVM && isDstVM;
        if (isVM2VM) {
            document
                .querySelector("#addOutboundForSourceContainer")
                .classList.remove("d-none");
            document
                .querySelector("#addInboundForDestinationContainer")
                .classList.remove("d-none");
            document.querySelector("#addOutboundForSource").disabled = false;
            document.querySelector(
                "#addInboundForDestination"
            ).disabled = false;
            document.querySelector("#addOutboundForSource").checked = false;
            document.querySelector("#addInboundForDestination").checked = false;
        } else if (isSrcVM) {
            document
                .querySelector("#addOutboundForSourceContainer")
                .classList.remove("d-none");
            document
                .querySelector("#addInboundForDestinationContainer")
                .classList.add("d-none");
            document.querySelector("#addOutboundForSource").disabled = true;
            document.querySelector("#addInboundForDestination").disabled = true;
            document.querySelector("#addOutboundForSource").checked = true;
            document.querySelector("#addInboundForDestination").checked = false;
        } else if (isDstVM) {
            document
                .querySelector("#addOutboundForSourceContainer")
                .classList.add("d-none");
            document
                .querySelector("#addInboundForDestinationContainer")
                .classList.remove("d-none");
            document.querySelector("#addOutboundForSource").disabled = true;
            document.querySelector("#addInboundForDestination").disabled = true;
            document.querySelector("#addOutboundForSource").checked = false;
            document.querySelector("#addInboundForDestination").checked = true;
        }

        window.createSecurityRuleInfo = {
            src: src,
            dst: dst,
        };

        clearMessagesFrom(document.querySelector("#createSecurityRuleModal"));
        updateSecurityRuleVisibility();
        window.CreateSecurityRuleModal.show();
    }

    function setDragEvents(el) {
        el.draggable = true;
        el.addEventListener('dragstart', function(ev) {            
            ev.dataTransfer.setData(
                "text/plain",
                JSON.stringify(getNodeType(this))
            );
            ev.dataTransfer.setDragImage(dragimg, 16, 16);   
            ev.dataTransfer.effectAllowed = "all";
            ev.stopPropagation();
        });
        el.addEventListener('dragend', function(ev) {
            ev.stopPropagation();            
        });
        el.addEventListener('dragenter', function (ev) {            
            ev.preventDefault();            
        });
        el.addEventListener('dragover', function (ev) {            
            ev.preventDefault();            
        });
        el.addEventListener('drop', function (ev) {
            console.log("ondrop", ev);
            ev.stopPropagation();
            ev.preventDefault();            
            const src = JSON.parse(ev.dataTransfer.getData("text/plain"));
            const dst = getNodeType(this);
            if (deepEqual(src, dst)) {
                console.log("src == dst. Ignore creating link", src, dst);
                return;
            }
            if (src.type != "vm" && dst.type != "vm") {
                console.log(
                    "src is not vm and dst is not vm. Ignore creating link",
                    src,
                    dst
                );
                return;
            }
            console.log("prepareCreateLink(", src, ",", dst, ")");

            prepareCreateLink(src, dst);
        });        
    }

    document
        .querySelectorAll(".vm,.subnet,.vpc,.network:not(#add-network)")
        .forEach(setDragEvents);

    // add network
    document
        .getElementById("submitNetworkAddress")
        .addEventListener("click", () => {
            const networkAddressInput =
                document.getElementById("networkAddress");
            const networkAddress = networkAddressInput.value.trim();
            console.log(networkAddress);
            const networkRegex =
                /^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))$/;
            const networkElements = document.querySelectorAll(".network");
            const lastNetworkElement =
                networkElements[networkElements.length - 1];
            const lastNetworkAddress = lastNetworkElement.dataset.address;

            if (!networkRegex.test(networkAddress)) {
                networkAddressInput.classList.add("is-invalid");
                networkAddressInput.addEventListener("input", () => {
                    if (networkRegex.test(networkAddressInput.value.trim())) {
                        networkAddressInput.classList.remove("is-invalid");
                    }
                });
                return;
            }

            const networkDiv = document.createElement("div");
            networkDiv.classList.add("network");
            const networkText = document.createElement("p");
            networkDiv.dataset.address = networkAddress;
            networkText.innerHTML = `<i class="fa-solid fa-globe"></i> ${networkAddress}`;
            networkDiv.appendChild(networkText);

            lastNetworkElement.parentNode.insertBefore(
                networkDiv,
                lastNetworkElement
            );
            setDragEvents(networkDiv);
            window.NetworkAddressModal.hide();
            networkAddressInput.value = "";
        });

    // setup windows
    document.querySelectorAll(".draggable").forEach((element) => {
        addHideButton(element);
        makeMoving(element);
        makeResizable(element, 200, 200);
    });
}
