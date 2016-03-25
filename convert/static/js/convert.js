var convert_home_js = (function($){
    // init drag file uploader
    var init_video_parts = function(){
        var _drag_container = document.getElementById('drag-file-container');
        var _video = document.getElementById('video-prop');
        var _video_drag_slider = document.getElementById('video-control-drag');
        var _timeout_id, _video_start_time = 0, _video_end_time = 5, _video_duration = 30;
        var _youtube_player, _youtube_video_id, _video_played = false;
        var _upload_file_handle, _current_video_type;

        // when meta data for the video is loaded
        _video.onloadedmetadata = function() {     
            _video_duration = _video.duration;
            _video_start_time=0;
            _video_end_time=5
            _reset_video_slider(_video_duration);
        };

        // when video play
        _video.onplay = function(){
            if( !_video_played ){
                _video_played = true;

                $('#video-control-drag').fadeIn();
                $('.file-uploader-footer').fadeIn();
            }
        }

        // video drag envet
        _drag_container.ondragover = function (event) {
            event.preventDefault();
            event.stopPropagation();
            return false; 
        };

        _drag_container.ondragend = function (event) {
            event.preventDefault();
            event.stopPropagation();
            return false; 
        };

        _drag_container.ondrop = function (event) { 
            event.preventDefault();
            event.stopPropagation();
 
            reset_video_from_page();

            var files = event.dataTransfer.files;
            _upload_file_handle = files[0];       
            _read_video_blob_data(_upload_file_handle)
        }; 

        // create video slider
        noUiSlider.create(_video_drag_slider, {
            start: [ _video_start_time, _video_end_time ],
            behaviour: 'drag',
            connect: true,
            margin: 1,
            step : 1,
            tooltips: [ wNumb({ decimals: 0 }), wNumb({ decimals: 0 }) ],
            range: {
                'min':  0,
                'max':  _video_duration
            }
        });

        // listening the video slider evnet 
        _video_drag_slider.noUiSlider.on('change', function( data, handle){
            _video_start_time = data[0],
            _video_end_time = data[1];

            if(_current_video_type == 'youtube'){
                _youtube_player.loadVideoById({
                    videoId:_youtube_video_id, 
                    startSeconds:_video_start_time
                });

                // clear timeout
                clearTimeout(_timeout_id);
                // paused when reach the end time
                _timeout_id = setTimeout(function(){ 
                    _youtube_player.pauseVideo();
                }, (_video_end_time-_video_start_time+1)*1000);
            }else{                        
                // clear timeout
                clearTimeout(_timeout_id);

                // set start time
                _video.currentTime = _video_start_time;
                _video.play();

                // paused when reach the end time
                _timeout_id = setTimeout(function(){ 
                    _video.pause();
                }, (_video_end_time-_video_start_time+1)*1000);
            }
        });


        // test browser support
        var _test_browser = function(){
            // test browser support html5 video or not
            var test_env = {
                filereader: typeof FileReader != 'undefined',
                dnd: 'draggable' in document.createElement('span'),
                formdata: !!window.FormData,
                progress: "upload" in new XMLHttpRequest
            };

            "filereader formdata progress".split(' ').forEach(function (api) {
                if (test_env[api] === false) {
                    alert('do not support drag upload!');
                }
            });
        }

        // reset all div
        var _reset_all_elements = function(){
            $('.video-convert-result').hide();
            $('.video-progress-bar-wrap').hide();
            $('#video-control-drag').hide();
            $('.file-uploader-footer').hide();

            $('#drag-file-container').show();
            
            if(_current_video_type == 'video'){
                $('#vp-mp4').attr('src', '');
                $('#video-prop').hide();
                _video.load();
            }else if(_current_video_type == 'youtube'){
                if(_youtube_player && _youtube_player.f != null){
                    _youtube_player.destroy();
                }
            }        
        }

        // send uploaded video data to server
        var send_request = function(form_data){
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/convert/video');

            xhr.upload.onloadstart = function (event) {
                $('.video-progress-bar-wrap').show();
                $('.video-convert-result').hide();
                $('.vup-text').text('Converting...');
            }

            xhr.upload.onprogress = function (event) {
                if (event.lengthComputable) {
                    var complete_percentage = (event.loaded / event.total * 100 | 0);
                    $('.video-upload-progress').width(complete_percentage+'%');
                }
            }

            xhr.onload = function(result) {
                var res_json = jQuery.parseJSON(xhr.responseText);
                if(!res_json.error){
                    $('.video-convert-result').show();
                    $('.video-progress-bar-wrap').hide();

                    $('.vcr-a').attr('href', res_json.response_file).text(res_json.response_file);
                    $('.generate-video-gif').attr('data-local-file', res_json.local_file);
                }
            };

            xhr.send(form_data);
        }

   
        // generate gif from video
        var generate_gif = function(event){
            var _gif_time_length = _video_end_time - _video_start_time,
                local_file = $('.generate-video-gif').attr('data-local-file');
            var form_data = new FormData();
            
            if(_current_video_type == 'video'){
                if( $('#vp-mp4').attr('src') == '' ){
                    swal({
                        title: "Error!",
                        text: "Please upload a video first.",
                        type: "error",
                        confirmButtonText: "Cool" 
                    });       
                    return;
                }
            }
            

            form_data.append('start_timestamps', _video_start_time);
            form_data.append('gif_duration', _gif_time_length);
            form_data.append('local_file', local_file);

            if(_current_video_type == 'video'){
                form_data.append('file', _upload_file_handle);
                form_data.append('type', 'video');
            }else if(_current_video_type == 'youtube'){
                form_data.append('type', 'youtube');
                form_data.append('youtube_id', _youtube_video_id);
            }
           
            send_request(form_data);
        }

        // upload file trigger event
        var upload_file_trigger = function(){
            $('#upload-file-input').trigger('click');
        }

        // upload file
        var upload_file = function(event){
            var files = document.getElementById('upload-file-input').files;
            _upload_file_handle = files[0];

            reset_video_from_page();
            _read_video_blob_data(_upload_file_handle);
        }


        // reset video slider 
        var _reset_video_slider = function(duration){
            // update video slider range
            _video_drag_slider.noUiSlider.set([_video_start_time, _video_end_time]);
            _video_drag_slider.noUiSlider.updateOptions({
                range: {
                    'min': 0,
                    'max': parseInt(duration)
                }
            });
        }

        // display related video div 
        var _show_related_video_elements = function(){
            if(_current_video_type == 'video'){
                $('#video-prop').show();           

                $('#player-youtube').hide();
                $('#drag-file-container').hide();
                if(_youtube_player && _youtube_player.f != null){
                    _youtube_player.destroy();
                }
            }else if(_current_video_type == 'youtube'){
                $('#player-youtube').show();

                $('#video-prop').hide();              
                $('#drag-file-container').hide();
            }
        }


        // read video blob data
        var _read_video_blob_data = function(file){
            var reader = new FileReader(),
                mime = file.type;

            // only support mp4 video
            if(mime != 'video/mp4'){
                swal({
                    title: "Error!",
                    text: "Sorry, we only support mp4 video!",
                    type: "error",
                    confirmButtonText: "Cool" 
                });      
                return;
            }

            // read video data as buffer
            reader.readAsArrayBuffer(file);

            // The load event is fired when a resource and its dependent resources have finished loading.
            reader.onload = function(evt) {
                if (evt.target.readyState == FileReader.DONE) { 
                    var blob = new Blob([evt.target.result], {type: mime}),     
                        video_blob_url = (URL || webkitURL).createObjectURL(blob);
                  
                    _show_video_preview(video_blob_url);
                }
            }  
        }

        // show video preview
        var _show_video_preview = function(video_blob_url){
            _current_video_type = 'video';
            _video_played = false;
            $('.generate-video-gif').attr('data-local-file', '');
            $('.file-uploader-footer').hide();

            // set the video source
            $('#vp-mp4').attr('src', video_blob_url);
            _video.load();
            
            // display related video div
            _show_related_video_elements();
        }


        // reset/remove video from page
        var reset_video_from_page = function(event){
            _reset_all_elements();
        }

        // add a video link
        var add_video_link = function(event){
            var $obj = $(event.target),
                video_link = $obj.closest('.modal-content').find('.video-add-link-input').val();

            if(video_link==''){
                swal({
                    title: "Error!",
                    text: "Sorry, your video link is invalid, please try another one.",
                    type: "error",
                    confirmButtonText: "Cool" 
                });      
                return;
            }

            $obj.closest('.modal-content').find('.video-add-link-input').val('');
            $('#video-control-drag').hide();
            $('.video-convert-result').hide();
            $('.file-uploader-footer').hide();

            _youtube_video_id = video_link.replace(/.*\?v=/, '');
            load_youtube_video(_youtube_video_id);

            // close modal
            $('#video-add-link').modal('hide')
        }  


        // load youtube video
        var load_youtube_video = function(_youtube_video_id){
            _current_video_type = 'youtube';
            _video_played = false;
            $('.generate-video-gif').attr('data-local-file', '');

            if(_youtube_player && _youtube_player.f != null){
                _youtube_player.destroy();
            }
            
            // load new youtube video
            _youtube_player = new YT.Player('player-youtube', {
                height: '300',
                videoId: _youtube_video_id,
                events: {
                    'onReady': youtube_ready_play,
                    'onStateChange': youtube_state_change
                }
            });

            // display related video div
            _show_related_video_elements();
        }


        // youtube video load
        var init_youtube_video_libs = function(){
            var tag = document.createElement('script');
            var firstScriptTag = document.getElementsByTagName('script')[0];

            tag.src = "https://www.youtube.com/iframe_api";
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);       
        }

        // The API will call this function when the video player is ready.
        var youtube_ready_play = function (event) {
            event.target.pauseVideo();
        }

        // if youtube finished load
        var youtube_state_change = function(event){
            if (event.data == YT.PlayerState.PLAYING && !_video_played) {
                _video_played = true;

                // reset video slider
                _video_start_time=0;
                _video_end_time=5
                _reset_video_slider(_youtube_player.getDuration());     

                $('#video-control-drag').fadeIn();
                $('.file-uploader-footer').fadeIn();
            }
        }

        return {
            load : function(){
                _test_browser();
                init_youtube_video_libs();
                $('.generate-video-gif').on('click', generate_gif);
                $('.reset-video').on('click', reset_video_from_page);
                $('.upload-file-bottom').on('click', upload_file_trigger);
                $('#upload-file-input').on('change', upload_file);
                $('.video-add-link-button').on('click', add_video_link);
            }
        }
    }

    // content scroll 
    var init_content_scroll = function(){
        window.sr = ScrollReveal({
            reset:true
        }).reveal('.wrap-3, .wrap-4, .wrap-5');

        sr.reveal('.top-content-1', {
            delay    : 200,
            distance : '90px',
            origin : 'bottom',
            scale    : 1.1
        });

        sr.reveal('.top-content-2', {
            delay    : 200,
            origin : 'top',
            distance : '90px',
            scale    : 1.1
        });
    }

    // init image scroll
    var init_image_scroll = function(){
        $('.img-scroll-holder').imageScroll({
            coverRatio: 0.5
        });
    }

    // init carousel
    var init_carousel = function(){
        $('.owl-carousel').owlCarousel({
            loop:true,
            margin:10,
            nav:false,
            responsive:{
                0:{
                    items:1
                },
                600:{
                    items:3
                },
                1000:{
                    items:5
                }
            }
        })
    }

    return {
        bind : function(){

        },
        init : function(){
            init_video_parts().load();
            init_content_scroll();
            init_image_scroll();
            init_carousel();
        }
    }
})($);