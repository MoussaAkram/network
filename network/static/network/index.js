document.addEventListener('DOMContentLoaded', function() {
    preparePosts();
});

function preparePosts() {
    let editButtons = document.querySelectorAll('.edit-post');
    editButtons.forEach((button) => {
        button.addEventListener('click', () => {
            let post = button.closest('.border');
            editPostContent(post);
        });
    }); 
    let likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach((button) => {
        button.addEventListener('click', () => {
            toggleLike(button);
        });
    });
}

function editPostContent(post) {
    let postText = post.querySelector('.post-text');
    let editButton = post.querySelector('.edit-post');
    let postId = post.querySelector(".post-id").value;

    let originalContent = postText.innerText;
    editButton.disabled = true;

    const editDiv = document.createElement('div');
    editDiv.innerHTML = `
        <textarea name="text" class="form-control mb-2" placeholder="Body" id="edited-post" rows="4">${originalContent}</textarea>
        <div class="d-flex justify-content-center ">
            <div><button type="button" class="btn btn-primary save-edit">Save</button></div>
            <div class="col"><span class="cancel-edit-post btn btn-secondary">Cancel</span></div>
        </div>
    `;

    postText.replaceWith(editDiv);

    let cancelEdit = editDiv.querySelector('.cancel-edit-post');
    let saveEdit = editDiv.querySelector('.save-edit');

    cancelEdit.addEventListener('click', cancelEditAction);
    saveEdit.addEventListener('click', () => sendEdit(postId, editDiv, postText, editButton, originalContent));

    function cancelEditAction() {
        editDiv.replaceWith(postText);
        editButton.disabled = false;
    }

    function sendEdit(postId, editDiv, postText, editButton, originalContent) {
        let newContent = editDiv.querySelector('#edited-post').value;

        fetch(`/edit/${postId}`, {
            method: 'POST',
            body: JSON.stringify({
                edited_text: newContent,
            }),
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            if (data.success) {
                restoreView(newContent, editDiv, postText, editButton);
            } else {
                restoreView(originalContent, editDiv, postText, editButton);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            restoreView(originalContent, editDiv, postText, editButton);
        });
    }

    function restoreView(content, editDiv, postText, editButton) {
        editDiv.replaceWith(postText);
        postText.innerText = content;
        editButton.disabled = false;
    }
}




function toggleLike(button) {
    let postId = button.dataset.postId;
    fetch(`/like/${postId}`, {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
       
    })
    .then(data => {
        let likeCountElement = button.querySelector('.like-count');
        if (likeCountElement) {
            likeCountElement.innerText = data.like_count;
        }
        if (data.liked) {
            button.querySelector('.like-icon').innerHTML = '&#10084;'; // Liked icon

        } else {
            button.querySelector('.like-icon').innerHTML = '&#129293;'; // Like icon

        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
