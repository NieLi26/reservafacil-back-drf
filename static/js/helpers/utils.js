// function pluralWord(validation, word = '') {
//     return validation ? word : ''
// }
const pluralWord = (validation, word = "") => (validation ? word : "");

// function formatDate(item) {
//     return item < 10 ? `0${item}` : item
// }

const formatDate = (item) => (item < 10 ? `0${item}` : item);

const formatTime = (item) => `${item}:00`;

// VALIDATIONS
function validarEmail(email) {
  const regex = /^\w+([.-_+]?\w+)*@\w+([.-]?\w+)*(\.\w{2,10})+$/;
  const resultado = regex.test(email);
  return resultado;
}

