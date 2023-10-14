/* VALIDAR DUPLICIDAD DE RUT */
// async function validateRutExists(rut) {
//   const url = "validate_rut.php";
//   const options = {
//     method: "POST",
//     mode: "same-origin",
//   };
//   const formData = new FormData();
//   formData.append("rut", rut);
//   options["body"] = formData;

//   return fetch(url, options)
//     .then((response) => response.text())
//     .catch((error) => console.log(error.message));
// }

/* VALIDAR FORMATO DE RUT */
function cleanRut(rut) {
    return typeof rut === "string"
      ? rut.replace(/^0+|[^0-9kK]+/g, "").toUpperCase()
      : "";
}
  
function validateRut(rut) {
    if (typeof rut !== "string") {
        return false;
    }

    // if it starts with 0 we return false
    // so a rut like 00000000-0 will not pass
    if (/^0+/.test(rut)) {
        return false;
    }

    if (!/^\d{7,8}-[\dkK]$/.test(rut)) {
        return false;
    }

    rut = cleanRut(rut);

    let t = parseInt(rut.slice(0, -1), 10);
    let m = 0;
    let s = 1;

    while (t > 0) {
        s = (s + (t % 10) * (9 - (m++ % 6))) % 11;
        t = Math.floor(t / 10);
    }

    const v = s > 0 ? "" + (s - 1) : "K";
    return v === rut.slice(-1);
}
