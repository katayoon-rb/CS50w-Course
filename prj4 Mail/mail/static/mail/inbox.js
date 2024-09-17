const recipients = document.querySelector('#compose-recipients')
const subject = document.querySelector('#compose-subject')
const body = document.querySelector('#compose-body')

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'))
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'))
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'))
    document.querySelector('#compose').addEventListener('click', compose_email)
    document.querySelector('#compose-view').addEventListener('submit', send_email)
    load_mailbox('inbox')
});

function load_mailbox(mailbox) {
    document.querySelector('#emails-view').style.display = 'block'
    document.querySelector('#emails-detail-view').style.display = 'none'
    document.querySelector('#compose-view').style.display = 'none'
    document.querySelector('#emails-view').innerHTML = `
        <h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>
    `

    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        emails.forEach(email => {
            const newEmail = document.createElement('div')
            newEmail.className = `list-group-item d-flex justify-content-between`
            newEmail.style.background =  email.read ? '#d7d7d7' : '#fff'
            newEmail.innerHTML = `
                <div>
                    <h6>Sender: ${email.sender}</h6>
                    <h4>Subject: ${email.subject}</h4>
                </div>
                <p>${email.timestamp}</p>
            `
            newEmail.addEventListener('click', () => view_email(email.id))
            document.querySelector('#emails-view').append(newEmail)
        })
    }) 
}

function view_email(id) {
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
        email_detail = document.querySelector('#emails-detail-view')
        document.querySelector('#emails-view').style.display = 'none'
        document.querySelector('#compose-view').style.display = 'none'
        email_detail.style.display = 'block'
        email_detail.innerHTML = `
            <ul class="list-group">
                <li class="list-group-item">
                    <strong>From: </strong>${email.sender}
                </li>
                <li class="list-group-item">
                    <strong>To: </strong>${email.recipients}
                </li>
                <li class="list-group-item">
                    <strong>Subject: </strong>${email.subject}
                </li>
                <li class="list-group-item">
                    <strong>Timestamp: </strong>${email.timestamp}
                </li>
                <li class="list-group-item">
                    ${email.body}
                </li>
            </ul>
        `
        
        if (!email.read) {
            fetch(`/emails/${email.id}`, {
                method: 'PUT',
                body: JSON.stringify({ read: true })
            })
        }

        const btns = document.createElement('div')
        btns.id = 'detail-btn-id'
        btns.className = 'w-25 mt-4 mx-auto d-flex align-items-center justify-content-center'
        document.querySelector('#emails-detail-view').append(btns)

        const btnArch = document.createElement('button')
        btnArch.className = `mx-2 btn ${!email.archived ? 'btn-success' : 'btn-danger'}`
        btnArch.innerHTML = !email.archived ? 'archive' : 'unarchive'
        btnArch.addEventListener('click', () => {
            fetch(`/emails/${email.id}`, {
                method: 'PUT',
                body: JSON.stringify({ archived: !email.archived })
            })
            .then(() => { load_mailbox('archive') })
        })
        btns.append(btnArch)

        const btnReply = document.createElement('button')
        btnReply.className = `mx-2 btn btn-info`
        btnReply.innerHTML = 'Reply'
        btnReply.addEventListener('click', () => {
            compose_email()
            let subj = email.subject
            if (subj.split(' ', 1)[0] != 'Re:') {
                subj = 'Re: ' + email.subject
            }

            recipients.value = email.sender
            subject.value = subj
            body.value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`
        })
        btns.append(btnReply)
    });
}

function compose_email() {
    document.querySelector('#emails-view').style.display = 'none'
    document.querySelector('#emails-detail-view').style.display = 'none'
    document.querySelector('#compose-view').style.display = 'block'
    recipients.value = ''
    subject.value = ''
    body.value = ''
}

function send_email(event) {
    event.preventDefault()
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: recipients.value,
            subject: subject.value,
            body: body.value
        })
    })
    .then(response => response.json())
    .then(result => { load_mailbox('sent') })
}
