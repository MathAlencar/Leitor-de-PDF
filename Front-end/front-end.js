

const buttonEnviarPDFs = document.querySelector('#buttonNome');
const baixando = document.querySelector('#buttonDownload');
const exibindoPDF = document.querySelector('.img-pdf');
const section = document.querySelector('section');
const menu = document.querySelector('.nav-side');
const buttonAppearMenu = document.querySelector('.menu-hamburgue');
const buttonXMenu = document.querySelector('.icone-x');

const load_01 = document.querySelector('#hr_1');
const load_block = document.querySelector("#load_block");

const frasesMotivacionais = [
    "Boa meninas! Quebrando barreiras, alcançando resultados! ✨",
    "Time de crédito, sempre em alta! 😎",
    "Boa meninas! Vocês são FODA! 🔥",
    "Isso ae garotas, determinação e foco, a receita do sucesso! 💪",
    "Isso ae, tem que vestir a camisa! 💪",
    "Isso aí Guerreiras! ⚔️",
    "Hulk esmaga! 👊💃",
    "Boas meninas, arrasando por aí! 😎🔥",
    "A força está com vocês! 💪✨",
    "Superando desafios, crescendo juntas! 📈",
    "Vamos que vamos, com garra e determinação! 🦁",
    "O sucesso é nosso destino! 🎯",
    "Boaaaaa, Inspirando e transformando 💫",
    "Mais um pra conta! 😎",
];

let tempFilePath = '';

function criandoDiv(classe){
    let div = document.createElement('div');
    div.setAttribute('class', classe)
    return div;
}

function criandoP(classe, nameArquivo){
    let p = document.createElement('p');
    p.setAttribute('class', classe)
    p.innerHTML = nameArquivo.slice(0, 15);
    return p;
}

function criandoIMG(classe, url){
    let img = document.createElement('img');
    img.setAttribute('class', classe);
    img.setAttribute('src', url);
    return img;
}

function NomePDF(){
    const formulario = document.querySelector('#formularioUser');

    const arquivosPDF = formulario.querySelector('input[type="file"]').files;

    exibindoPDF.innerHTML = ''

    if(arquivosPDF.length > 0){
        for(let i=0; i< arquivosPDF.length; i++){
            const arquivo = arquivosPDF[i];
            
            let div_pai = criandoDiv('iconeArquivo');
            let div_filho_1 = criandoDiv('null');
            let div_filho_2 = criandoDiv('null');
            let img = criandoIMG('imgPDF', 'https://cdn-icons-png.flaticon.com/128/4726/4726010.png');
            let criandoPara = criandoP('null', arquivo.name);

            div_filho_1.appendChild(img);
            div_filho_2.appendChild(criandoPara);
            div_pai.appendChild(div_filho_1);
            div_pai.appendChild(div_filho_2);

            exibindoPDF.appendChild(div_pai);
        }
    }
}

function exibindoMenu(){
    section.style.marginLeft = '15rem'
    menu.style.display = 'flex'
    menu.style.width = '15rem'
}

function escondendoMenu(){
    section.style.marginLeft = '0rem'
    menu.style.width = '0rem'
}

function load_blocks(opc){
    switch (opc) {
        case 1:
            load_block.setAttribute('class', 'load');
            break;
        case 2:
            load_block.setAttribute('class', 'block');
            break;
        default:
    }
}


buttonAppearMenu.addEventListener('click', (e) => {
    exibindoMenu();
    buttonAppearMenu.style.display = 'none'
})

buttonXMenu.addEventListener('click', (e) => {
        escondendoMenu();
        buttonAppearMenu.style.display = 'block'
})

buttonEnviarPDFs.addEventListener('click', (e) => {
    e.preventDefault();

    exibindoPDF.innerHTML =  ''

    let formulario = document.querySelector('#formularioUser');
    const form = new FormData(formulario);

    let arquivosPDF = formulario.querySelector('input[type="file"]').files;
    load_blocks(1)

    // Validando se Todos são ou não PDF's

    if(arquivosPDF.length > 0){
        for(let i=0; i< arquivosPDF.length; i++){
            const arquivo = arquivosPDF[i];
            
            if(arquivo.type != 'application/pdf') {
                mostrarAlertaError(`O arquivo ${arquivo.name} não é um PDF válido.`)
                continue
            }

            form.append('arquivos[]', arquivo);
        }
    }

    try{
        fetch('http://127.0.0.1:5000/upload/pdfs', {
            method: "POST",
            body: form
        })
        .then(response => response.json())
        .then(data => {
            load_blocks(2)

            if(data.menssage == 'Nenhum arquivo foi enviado!'){
                mostrarAlertaError(`${data.menssage} 😡`);
            }else {
                let numeroAleatorio = gerarNumeroAleatorio(1, 10);
                console.log(numeroAleatorio)
                mostrarAlertaSucesso(frasesMotivacionais[numeroAleatorio]);
                mostrarAlertaSucesso(`${data.menssage} 👍`);
            }
            
            arquivosPDF = formulario.querySelector('input[type="file"]');
            arquivosPDF.value = '';

            tempFilePath = data.temp_file
        })
        .catch(error => {
            load_blocks(2)
            mostrarAlertaError('A requisição deu um erro inesperado, contate o desenvolvedor (matheus) :V !');
        })
    }  
    catch{
        mostrarAlertaError('A requisição deu um erro inesperado, contate o desenvolvedor (matheus) :V !')
        load_blocks(2)
    }
})

baixando.addEventListener('click', (e) => {
    e.preventDefault()

    exibindoPDF.innerHTML = ""

    if(!tempFilePath){
        mostrarAlertaError('Nenhum arquivo foi enviado ainda! 😡')
        return
    }
    try{
        fetch(`http://127.0.0.1:5000/download_xlsx?file=${encodeURIComponent(tempFilePath)}`, {
            method: "GET",
        })
        .then(response => {
            if(response.ok) {
                return response.blob();
            } else {
                throw new Error('Erro ao baixar o arquivo.');
            }
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'Extratos.xlsx';
            document.body.appendChild(a);
            a.click();  // Simula o clique no link para iniciar o download
            window.URL.revokeObjectURL(url);  // Limpa o objeto URL
            tempFilePath = ''
        })
        .catch(error => {
            console.log('não deu bom.')
        })
    }
    catch{
        mostrarAlertaError('A requisição deu um erro inesperado, contate o desenvolvedor (matheus) :V !')
    }
})

function mostrarAlertaSucesso(mensagem) {
    alertify.success(mensagem);
}

function mostrarAlertaError(mensagem) {
    alertify.error(mensagem);
}

function gerarNumeroAleatorio(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}




// http://192.168.1.224:4222
// http://192.168.1.224:4222