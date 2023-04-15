// global variables for last id instead of trigger-id (unused)
var g_interaction_id, g_reply_id, g_post_id;

function countText() {
    let text = document.count_text.text.value;
    document.getElementById('characters').innerText = text.length;
    //document.getElementById('words').innerText = text.length == 0 ? 0 : text.split(/\s+/).length;
    //document.getElementById('rows').innerText = text.length == 0 ? 0 : text.split(/\n/).length;
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

// attach id="reply_id" to the last element so ajax can get it for the next call?
function ajax_get_replies(reply_id) {
  console.log(reply_id);
  $.ajax({url: "/reply_scroll/" + reply_id, 
  beforeSend: function(){
    $("#loading-reply").show();
  },
  success: function(result){
    //console.log(result);
    let before_id = reply_id;
    let posts_to_load = 5;
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

      if (is_liked === false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like");
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red");
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#replies-container");
      before_id = post_id;
    }

    $('[id^="trigger-"]').attr('id', "trigger-"+before_id).appendTo("#"+before_id);

    if (result.length < posts_to_load){
      console.log(result.length);
      $("#loading-reply").remove();
      $('[id^="trigger-"]').remove();
    }
  }
});
}

function ajax_get_posts(post_id) {
  console.log(post_id);
  $.ajax({url: "/post_scroll/" + post_id, 
  beforeSend: function(){
    $("#loading-post").show();
  },
  success: function(result){
    //console.log(result);
    let before_id = post_id;
    let posts_to_load = 5;
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

      if (is_liked === false){
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();"})
        .removeClass().addClass("btn bi bi-heart post-icon tt like");
      }
      else{
        new_div.find("#like-"+before_id).attr({'id': "like-"+post_id, 'onclick': "ajax_like("+post_id+");event.stopPropagation();"})
        .removeClass().addClass("btn bi bi-heart-fill post-icon tt like fill-red");
      }

      new_div.find("#like_count-"+before_id).attr('id', "like_count-"+post_id).text(like_count);
      new_div.find("#reply_count-"+before_id).attr('id', "reply_count-"+post_id).text(reply_count);

      new_div.find("#reply-btn").removeAttr('href').attr('onclick', "window.location='/post/"+post_id+"';event.stopPropagation();");
      new_div.appendTo("#posts-container");
      before_id = post_id;
    }
    
    $('[id^="trigger-"]').attr('id', "trigger-"+before_id).appendTo("#"+before_id);

    if (result.length < posts_to_load){
      console.log(result.length);
      $("#loading-post").remove();
      $('[id^="trigger-"]').remove();
    }
  }
});
}

function ajax_get_follows(interaction_id) {
  console.log(interaction_id);
  $.ajax({url: "/follow_scroll/" + interaction_id, 
  beforeSend: function(){
    $("#loading-follows").show();
  },
  success: function(result){
    console.log(result)
    let before_id = interaction_id;
    let follows_to_load = 5

    for(i in result){
    var new_div = $("#"+before_id).clone();

    }

    if (result.length < follows_to_load){
      console.log(result.length);
      $("#loading-follows").remove();
      $('[id^="trigger-"]').remove();
    }
  }
});
}

// listener for scrolling to element | remove trigger id from element when ajax_get_replies is called and re-add to a newer one if necessary
if(window.location.href.includes('/post/')){
  const el = document.querySelector('[id^="trigger-"]');
  if(el){
    const observer = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_replies((el.id).toString().slice(8));
            console.log(el.id)
        } else {
            console.log("not visible");
        }
    });

  observer.observe(el);
  }
}

if(window.location.href.includes('/user/') && !window.location.href.includes('/follow/')){
  const el = document.querySelector('[id^="trigger-"]');
  if(el){
    const observer = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_posts((el.id).toString().slice(8));
            console.log(el.id)
        } else {
            console.log("not visible");
        }
    });

  observer.observe(el);
  }
}

if(window.location.href.includes('/following')){
  const el = document.querySelector('[id^="trigger-"]');
  if(el){
    const observer = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting){
            ajax_get_follows((el.id).toString().slice(8));
            console.log(el.id)
        } else {
            console.log("not visible");
        }
    });

  observer.observe(el);
  }
}

// hide spinner after loading
$(document).ready(function() {
  $("#loading").hide();
});