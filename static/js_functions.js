// global variables for last id instead of trigger-id (unused)
var g_interaction_id, g_reply_id, g_post_id;

function countText() {
    let text = document.count_text.text.value;
    document.getElementById('characters').innerText = text.length;
    //document.getElementById('words').innerText = text.length == 0 ? 0 : text.split(/\s+/).length;
    //document.getElementById('rows').innerText = text.length == 0 ? 0 : text.split(/\n/).length;
  }

function ajax_follow(dynamic_user) {
  //console.log(dynamic_user);
  $.ajax({url: "/user/" + dynamic_user + "/follow", success: function(result){
    //console.log(result);
    if (result == "follow") {
      $("#follow-" + dynamic_user).text("Unfollow");
    } else if (result == "unfollow"){
      $("#follow-" + dynamic_user).text("Follow");
    }
  }});
}

function follow_alert(){
  alert("You must be logged in to Follow")
}

function ajax_like(post_id) {
  //console.log(post_id);
  $.ajax({url: "/post/" + post_id + "/like", success: function(result){
    //console.log(result);
    if (result == "like") {
      //console.log(result);
      $("#like-" + post_id).attr('data-bs-original-title', 'Unlike')
                .css("color", "red")
                .removeClass("bi-heart")
                .addClass("bi-heart-fill")
                .tooltip('update')
                .tooltip('show');
      $("#like_count-" + post_id).text(parseInt($("#like_count-"+post_id).text())+1);
    } else if (result == "unlike"){
      //console.log(result);
      $("#like-" + post_id).attr('data-bs-original-title', 'Like')
                .css("color", "white")
                .removeClass("bi-heart-fill")
                .addClass("bi-heart")
                .tooltip('update')
                .tooltip('show');
      $("#like_count-" + post_id).text(parseInt($("#like_count-"+post_id).text())-1);
    }
  }});
}

function like_alert(){
  alert("You must be logged in to like")
}

function reply_alert(){
  alert("You must be logged in to reply")
}

function ajax_get_replies(reply_id) {
  //console.log(reply_id);
  $.ajax({url: "/reply_scroll/" + reply_id, 
  success: function(result){
    //console.log(result);
    let before_id = reply_id;
    let posts_to_load = 10;
    for (i in result){
      let post_id = result[i]["post_id"];
      let user_name = result[i]["user_name"];
      let recency = result[i]["recency"];
      let text = result[i]["text"];
      let timestamp = result[i]["timestamp"];
      let is_liked = result[i]["is_liked"];
      let like_count = result[i]["like_count"];
      let reply_count = result[i]["reply_count"];
      
      // clone previous post div element and insert new data
      var new_div = $("#"+before_id).clone();
      new_div.attr('id', post_id)
      new_div.find("#reply-span").attr('onclick', "window.location='/post/"+post_id+"';");
      //new_div.find("#profile-picture").attr('src', "/static/images/kitten.jpg");
      new_div.find("#name").html(user_name).attr('onclick', "window.location='/user/"+user_name+"';event.stopPropagation();");
      new_div.find("#date").html(recency).attr('data-bs-original-title', timestamp).tooltip('update');
      new_div.find("#content-text").text(text);

      if (is_liked == false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Like"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like").tooltip('update');
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Unlike"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red").tooltip('update');
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#replies-container");
      before_id = post_id;
    }
    // move observer to end of page
    $('[id^="trigger-"]').attr('id', "trigger-"+before_id).appendTo("#"+before_id);

    if (result.length < posts_to_load){
      //console.log(result.length);
      $('[id^="trigger-"]').remove();
    }
  }
});
}

function ajax_get_user_replies(reply_id) {
  //console.log(reply_id);
  $.ajax({url: "/user_reply_scroll/" + reply_id, 
  success: function(result){
    //console.log(result);
    let before_id = reply_id;
    let posts_to_load = 10;
    for (i in result){
      let post_id = result[i]["post_id"];
      let user_name = result[i]["user_name"];
      let recency = result[i]["recency"];
      let text = result[i]["text"];
      let timestamp = result[i]["timestamp"];
      let is_liked = result[i]["is_liked"];
      let like_count = result[i]["like_count"];
      let reply_count = result[i]["reply_count"];

      var new_div = $("#"+before_id).clone();
      new_div.attr('id', post_id)
      new_div.find("#reply-span").attr('onclick', "window.location='/post/"+post_id+"';");
      //new_div.find("#profile-picture").attr('src', "/static/images/kitten.jpg");
      new_div.find("#name").html(user_name).attr('onclick', "window.location='/user/"+user_name+"';event.stopPropagation();");
      new_div.find("#date").html(recency).attr('data-bs-original-title', timestamp).tooltip('update');
      new_div.find("#content-text").text(text);

      if (is_liked == false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Like"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like").tooltip('update');
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Unlike"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red").tooltip('update');
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#replies-container");
      before_id = post_id;
    }

    $('[id^="trigger_replies-"]').attr('id', "trigger_replies-"+before_id).appendTo("#"+before_id);

    if (result.length < posts_to_load){
      //console.log(result.length);
      $('[id^="trigger_replies-"]').remove();
    }
  }
});
}

function ajax_get_posts(post_id) {
  //console.log(post_id);
  $.ajax({url: "/post_scroll/" + post_id,
  success: function(result){
    //console.log(result);
    let before_id = post_id;
    let posts_to_load = 10;
    for (i in result){
      let post_id = result[i]["post_id"];
      let user_name = result[i]["user_name"];
      let recency = result[i]["recency"];
      let text = result[i]["text"];
      let timestamp = result[i]["timestamp"];
      let is_liked = result[i]["is_liked"];
      let like_count = result[i]["like_count"];
      let reply_count = result[i]["reply_count"];
      //console.log(post_id, like_count);

      var new_div = $("#"+before_id).clone();
      new_div.attr('id', post_id)
      new_div.find("#post-span").attr('onclick', "window.location='/post/"+post_id+"';");
      //new_div.find("#profile-picture").attr('src', "/static/images/kitten.jpg");
      new_div.find("#name").html(user_name).attr('onclick', "window.location='/user/"+user_name+"';event.stopPropagation();");
      new_div.find("#date").html(recency).attr('data-bs-original-title', timestamp).tooltip('update');
      new_div.find("#content-text").text(text);

      if (is_liked == false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Like"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like").tooltip('update');
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Unlike"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red").tooltip('update');
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#posts-container");
      before_id = post_id;
    }
    
    $('[id^="trigger_posts-"]').attr('id', "trigger_posts-"+before_id).appendTo("#"+before_id);

    if (result.length < posts_to_load){
      //console.log(result.length);
      $('[id^="trigger_posts-"]').remove();
    }
  }
});
}

function ajax_get_likes(likes_id, post_id) {
  //console.log(likes_id);
  //console.log(post_id)
  $.ajax({url: "/likes_scroll/" + likes_id,
  success: function(result){
    //console.log(result);
    let before_id = post_id;
    let posts_to_load = 10;
    for (i in result){
      let post_id = result[i]["post_id"];
      let user_name = result[i]["user_name"];
      let recency = result[i]["recency"];
      let text = result[i]["text"];
      let timestamp = result[i]["timestamp"];
      let is_liked = result[i]["is_liked"];
      let like_count = result[i]["like_count"];
      let reply_count = result[i]["reply_count"];
      //console.log(post_id, like_count);

      var new_div = $("#"+before_id).clone();
      //console.log(new_div.id);
      new_div.attr('id', post_id)
      new_div.find("#post-span").attr('onclick', "window.location='/post/"+post_id+"';");
      //new_div.find("#profile-picture").attr('src', "/static/images/kitten.jpg");
      new_div.find("#name").html(user_name).attr('onclick', "window.location='/user/"+user_name+"';event.stopPropagation();");
      new_div.find("#date").html(recency).attr('data-bs-original-title', timestamp).tooltip('update');
      new_div.find("#content-text").text(text);

      if (is_liked == false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Like"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like").tooltip('update');
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Unlike"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red").tooltip('update');
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#likes-container");
      before_id = post_id;
    }
    
    if (result.length > 0){
      $('[id^="trigger_likes-"]').attr('id', "trigger_likes-"+result[i]["last_likes_id"]+"-"+post_id).appendTo("#"+before_id);
    }
    else{
      $('[id^="trigger_likes-"]').remove();
    }

    if (result.length < posts_to_load){
      //console.log(result.length);
      $('[id^="trigger_likes-"]').remove();
    }
  }
});
}

function ajax_get_timeline(post_id) {
  //console.log(post_id);
  $.ajax({url: "/home_scroll/" + post_id, 
  success: function(result){
    //console.log(result);
    //console.log(post_id);
    let before_id = post_id;
    let posts_to_load = 10;
    for (i in result){
      let post_id = result[i]["post_id"];
      let user_name = result[i]["user_name"];
      let recency = result[i]["recency"];
      let text = result[i]["text"];
      let timestamp = result[i]["timestamp"];
      let is_liked = result[i]["is_liked"];
      let like_count = result[i]["like_count"];
      let reply_count = result[i]["reply_count"];

      var new_div = $("#"+before_id).clone();
      new_div.attr('id', post_id)
      new_div.find("#post-span").attr('onclick', "window.location='/post/"+post_id+"';");
      //new_div.find("#profile-picture").attr('src', "/static/images/kitten.jpg");
      new_div.find("#name").html(user_name).attr('onclick', "window.location='/user/"+user_name+"';event.stopPropagation();");
      new_div.find("#date").html(recency).attr('data-bs-original-title', timestamp).tooltip('update');
      new_div.find("#content-text").text(text);

      if (is_liked == false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Like"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like").tooltip('update');
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();", 'data-bs-placement': "bottom", 'title': "Unlike"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red").tooltip('update');
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#posts-container");
      before_id = post_id;
    }
    
    $('[id^="trigger-"]').attr('id', "trigger-"+before_id).appendTo("#"+before_id);

    if (result.length < posts_to_load){
      //console.log(result.length);
      $('[id^="trigger-"]').remove();
    }
  }
});
}

function ajax_get_follows(interaction_id) {
  //console.log(interaction_id);
  $.ajax({url: "/follow_scroll/" + interaction_id, 
  success: function(result){
    //console.log(result)
    let before_id = interaction_id;
    let follows_to_load = 5

    for(i in result){
    var new_div = $("#"+before_id).clone();

    }

    if (result.length < follows_to_load){
      //console.log(result.length);
      $('[id^="trigger-"]').remove();
    }
  }
});
}

// listener for scrolling to element
if(window.location.href.includes('/post/')){
  const el = document.querySelector('[id^="trigger-"]');
  if(el){
    const observer = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_replies((el.id).toString().slice(8));
            //console.log(el.id)
        } else {
            //console.log("not visible");
        }
    });

  observer.observe(el);
  }
}

var page = window.location.pathname;
if(page == '/' || page == '/default.aspx'){
  const el = document.querySelector('[id^="trigger-"]');
  if(el){
    const observer = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_timeline((el.id).toString().slice(8));
            //console.log(el.id)
        } else {
            //console.log("not visible");
        }
    });

  observer.observe(el);
  }
}

if(window.location.href.includes('/user/') && !window.location.href.includes('/follow/')){
  const el1 = document.querySelector('[id^="trigger_posts-"]');
  const el2 = document.querySelector('[id^="trigger_likes-"]');
  const el3 = document.querySelector('[id^="trigger_replies-"]');
  if(el1){
    const observer1 = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_posts((el1.id).toString().slice(14));
            //console.log(el1.id)
        } else {
            //console.log("not visible");
        }
    });
  observer1.observe(el1);
  }
  if(el2){
    const observer2 = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            var [trigger, likes_id, post_id] = (el2.id).split('-');
            //console.log(likes_id)
            //console.log(post_id)
            ajax_get_likes(likes_id, post_id);
            //console.log(el2.id)
        } else {
            //console.log("not visible");
        }
    });
  observer2.observe(el2);
  }
  if(el3){
    const observer3 = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_user_replies((el3.id).toString().slice(16));
            //console.log(el3.id)
        } else {
            //console.log("not visible");
        }
    });
  observer3.observe(el3);
  }
}

if(window.location.href.includes('/following')){
  const el = document.querySelector('[id^="trigger-"]');
  if(el){
    const observer = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_follows((el3.id).toString().slice(8));
            //console.log(el.id)
        } else {
            //console.log("not visible");
        }
    });

  observer.observe(el);
  }
}

// hide spinner after loading
$(document).ready(function() {
  $("#loading").hide();
});