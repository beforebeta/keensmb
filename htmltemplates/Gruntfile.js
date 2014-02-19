'use strict';
var LIVERELOAD_PORT = 35729;
var lrSnippet = require('connect-livereload')({ port: LIVERELOAD_PORT });
var mountFolder = function (connect, dir) {
  return connect.static(require('path').resolve(dir));
};

// var proxySnippet = require('grunt-connect-proxy/lib/utils').proxyRequest;

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to recursively match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {
  require('load-grunt-tasks')(grunt);
  require('time-grunt')(grunt);

  // configurable paths
  var yeomanConfig = {
    app: '../keen/web/static',
    dist: 'dist'
  };

  try {
    yeomanConfig.app = require('./bower.json').appPath || yeomanConfig.app;
  } catch (e) {}

  grunt.initConfig({
    yeoman: yeomanConfig,
    watch: {
      // styles: {
      //   files: ['<%= yeoman.app %>/css/{,*/}*.css'],
      //   tasks: ['copy:styles']
      // },
      css: {
        files: '<%= yeoman.app %>/css/{,*/}*.css',
        tasks: [],
        options: {
          livereload: LIVERELOAD_PORT
        }
      },
      // less: {
      //   files: '<%= yeoman.app %>/less/*.less',
      //   tasks: ['less'],
      //   options: {
      //     livereload: LIVERELOAD_PORT,
      //     dumpLineNumbers: "comments",
      //     env: "development",
      //     relativeUrls: false
      //   }
      // },
      // livereload: {
      //   options: {
      //     livereload: LIVERELOAD_PORT
      //   },
      //   files: [
      //     '<%= yeoman.app %>/../templates/{,*/}*.html',
      //     '<%= yeoman.app %>/js/{,*/}*.js',
      //     '<%= yeoman.app %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
      //   ]
      // }
    },
    less: {
      development: {
        options: {
          paths: ['<%= yeoman.app %>/less'],
          yuicompress: true
        },
        files: {
          '<%= yeoman.app %>/css/flat-ui-custom.css': '<%= yeoman.app %>/less/flat-ui.less'
        }
      }
    },
    connect: {
      options: {
        port: 9001,
        hostname: '0.0.0.0'
      },
      livereload: {
        options: {
          middleware: function (connect) {
            return [
              // proxySnippet,
              lrSnippet,
              mountFolder(connect, yeomanConfig.app)
            ];
          }
        }
      }
    },
    open: {
      server: {
        url: 'http://localhost:<%= connect.options.port %>'
      }
    },
    concurrent: {
      server: [
        'copy:styles'
      ]
    }
  });

  grunt.registerTask('server', [
    // 'concurrent:server',
    // 'open:server',
    'connect:livereload',
    'watch'
  ]);

  grunt.registerTask('default', [
    'concurrent:server',
    'connect:livereload',
    'watch'
  ]);
};
