function countText() {
    let text = document.count_text.text.value;
    document.getElementById('characters').innerText = text.length;
    document.getElementById('words').innerText = text.length == 0 ? 0 : text.split(/\s+/).length;
    document.getElementById('rows').innerText = text.length == 0 ? 0 : text.split(/\n/).length;
  }

function ajax_follow(dynamic_user) {
  console.log(dynamic_user);
  $.ajax({url: "/user/" + dynamic_user + "/follow", success: function(result){
    console.log(result);
    if (result == "follow") {
      //console.log(result);
      //dynamic_user = dynamic_user.data
      $("#follow").text("Unfollow");
      //console.log(dynamic_user + " followed");
    } else if (result == "unfollow"){
      //console.log(result);
      //dynamic_user = dynamic_user.data
      $("#follow").text("Follow");
      //console.log(dynamic_user + " unfollowed");
    }
  }});
}

function ajax_like(post_id) {
  console.log(post_id);
  $.ajax({url: "/post/" + post_id + "/like", success: function(result){
    console.log(result);
    if (result == "like") {
      //console.log(result);
      $("#like_" + post_id).attr('data-bs-original-title', 'Unlike')
                .css("color", "red")
                .removeClass("bi-heart")
                .addClass("bi-heart-fill")
                .tooltip('update')
                .tooltip('show');
    } else if (result == "unlike"){
      //console.log(result);
      $("#like_" + post_id).attr('data-bs-original-title', 'Like')
                .css("color", "white")
                .removeClass("bi-heart-fill")
                .addClass("bi-heart")
                .tooltip('update')
                .tooltip('show');
    }
  }});
}

/*
function ajax_follow(dynamic_user) {
  console.log(dynamic_user);
  $.ajax({url: "/user/" + dynamic_user + "/follow", success: function(result){
    if (result == 'success') {
      console.log(result);
      dynamic_user = dynamic_user.data
      $("#follow").text("Unfollow");
      $("#follow").attr("onclick", "ajax_unfollow(dynamic_user)");
      console.log(dynamic_user + " followed");
    }
  }});
}

function ajax_unfollow(dynamic_user) {
  console.log(dynamic_user);
  $.ajax({url: "/user/" + dynamic_user + "/unfollow", success: function(result){
    if (result == 'success') {
      console.log(result);
      // what is the actual value of dynamic_user
      dynamic_user = dynamic_user.data
      $("#unfollow").text("Follow");
      $("#unfollow").attr("onclick", "ajax_follow(dynamic_user)");
      console.log(dynamic_user + " unfollowed");
    }
  }});
}
*/