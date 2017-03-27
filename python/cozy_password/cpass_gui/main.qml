import QtQuick 2.7
import QtQuick.Controls 1.5
import QtQuick.Controls.Styles 1.4
import QtQuick.Window 2.0

import PyResolver 1.0

ApplicationWindow {
    id: mwn

    readonly property real dpi: Screen.pixelDensity * 25.4
    readonly property bool high_resolution_desktop: Screen.pixelDensity > 3.77 ? Screen.pixelDensity < 4.92 ? true : false : false
    property real dp: high_resolution_desktop ? 1.25 : 1
    property int spacing: 8 * dp
    property int row_height: 40 * dp

    property var colors: {
        'red' : '#F44336',
                'pink' : '#E91E63',
                'purple' : '#9C27B0',
                'deeppurple' : '#673AB7',
                'indigo' : '#3F51B5',
                'blue' : '#2196F3',
                'lightblue' : '#03A9F4',
                'cyan' : '#00BCD4',
                'teal' : '#009688',
                'green' : '#4CAF50',
                'lightgreen' : '#8BC34A',
                'lime' : '#CDDC39',
                'yellow' : '#FFEB3B',
                'amber' : '#FFC107',
                'orange' : '#FF9800',
                'deeporange' : '#FF5722',
                'brown' : '#795548',
                'grey' : '#9E9E9E',
                'bluegrey' : '#607D8B',
                'blue100' : '#B3E5FC',
                'green100' : '#C8E6C9',
                'grey100' : '#F5F5F5'
    }
    property string border_color: colors.grey
    property int border_width: 1 * mwn.dp
    property bool login_succeeded: true

    //States begin
    readonly property string common: 'common'
    readonly property string password: 'password'
    readonly property string login: 'login'
    readonly property string pending: "pending"
    readonly property string ren: "ren"
    readonly property string cmd: "cmd"
    readonly property string add: "add"
    readonly property string set: "set"
    readonly property string addinfo: 'addinfo'
    readonly property string del: "del"
    readonly property string esc: 'esc'


    property string currentState: modes.initial

    function switch_state(newstate, text, placeholder, custom) {
        var o = {'state' : currentState}
        if (placeholder !== undefined) o.placeholder = placeholder
        if (text !== undefined) o.text = text
        if (custom !== undefined) o.custom = text
        actions_stack.push(o)
        currentState = newstate
    }

    function return_state() {
        var o = actions_stack.pop()
        currentState = o.state
        _enterField.placeholderText = o.placeholder !== undefined ? o.placeholder : ''
        _enterField.text = o.text !== undefined ? o.text : ''
        if (currentState === mwn.common) {
            modes[common].onTextChanged('')
        }
    }

    function glimpse_stack() {
        return actions_stack[actions_stack.length - 1]
    }

    function to_common() {
        //No need to swhitch unless we're there
        if (currentState === common) {
            return
        }
        var o;
        while (true) {
            if ((o = actions_stack.pop()).state === common) break
        }
        currentState = o.state
        _enterField.text = ''
        _enterField.placeholderText = ''
        modes[common].onTextChanged('')
    }

    property var commands : ([
                                 add, set, del, ren, esc
                             ])
    property var actions_stack : ([])
    property var modes:
        ({
             initial : login,
             login :
                 ({
                      model: [],
                      container :
                          ({
                               width: 70 * dp,
                               text: "login",
                           }),
                      passwordButton :
                          ({
                               visible : true
                           }),
                      tfstyle: _normalTFStyle,
                      echomode: (_passwordButton.pressed ? TextInput.Normal : TextInput.Password),
                      placeholder: "Password sir",
                      onTextChanged : function(text) {
                      },
                      onReturn : function() {
                          if (_resolver.check_password(_textField.text)) {
                              _resolver.password = _textField.text
                              _enterField.style = _normalTFStyle
                              switch_state(common, '', this.placeholder)
                              _enterField.text = ''
                              _enterField.placeholderText = ''
                              _resolver.sync()
                          } else {
                              _textField.text = ''
                              _enterField.style = _errorTFStyle
                              var oldtext = _enterField.placeholderText
                              _enterField.placeholderText = "Incorrect, sir"
                              delay(1000 ,function() {
                                  if (currentState == login) {
                                      _enterField.placeholderText = oldtext
                                      _enterField.style = _normalTFStyle
                                  }
                              })
                          }
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {},
                      onEscape : function() {
                          Qt.quit()
                      }
                  }),
             common :
                 ({
                      model : [],
                      container :
                          ({
                               width: 0,
                               text: ""
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode: TextInput.Normal,
                      placeholder: "",
                      onTextChanged : function (text) {
                          if (text[0] === ':') {
                              listModel = []
                              switch_state(cmd)
                              _enterField.text = _enterField.text.substring(1)
                          } else {
                              var keys = _resolver.keys
                              listModel = keys.filter(function(obj) {
                                  var rx = new RegExp(text, 'i')
                                  if (rx.test(obj)) {
                                      return true
                                  }
                                  return false
                              })
                          }
                      },
                      onReturn : function() {
                      },
                      onListIndexChanged : function(index) {
                          console.log("On commmon list index: " + index)
                      },
                      onListIndexAccepted : function(index) {
                          _resolver.k2p_clipboard(listModel[index])
                          _enterField.text = ''
                          mwn.hide()
                      },
                      onKeysChanged: function(keys) {
                          this.onTextChanged(_enterField.text)
                      },
                      onEscape : function() {
                          mwn.hide()
                      }
                  }),
             password :
                 ({
                      container :
                          ({
                               width: 115 * dp,
                               text: "password"
                           }),
                      passwordButton :
                          ({
                               visible : true
                           }),
                      tfstyle: _normalTFStyle,
                      echomode: (_passwordButton.pressed ? TextInput.Normal : TextInput.Password),
                      placeholder: '',
                      onTextChanged : function (text) {},
                      onReturn : function() {
                          var passwd = _enterField.text
                          var oldtext = _enterField.placeholderText
                          var o = glimpse_stack()
                          //Clean password dots
                          _enterField.text = ''
                          if (modes[o.state].onPassword({name: o.text, password: passwd})) {
                              _enterField.style = _successTFStyle
                              _enterField.placeholderText = 'Succeeded'

                          } else {
                              _enterField.style = _errorTFStyle
                              _enterField.placeholderText = 'Error'
                          }
                          delay(1000 ,function() {
                              _enterField.style = _normalTFStyle
                              to_common()
                          })
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {},
                      onEscape : function() {
                          return_state()
                      }
                  }),
             addinfo :
                 ({
                      container :
                          ({
                               width: 120 * dp,
                               text: "new name"
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode: TextInput.Normal,
                      placeholder: '',
                      onTextChanged : function (text) {},
                      onReturn : function() {
                          var lnewname = _enterField.text
                          var oldtext = _enterField.placeholderText
                          var o = glimpse_stack()
                          //Clean password dots
                          _enterField.text = ''
                          if (modes[o.state].onRename({oldname : o.text, newname: lnewname})) {
                              _enterField.style = _successTFStyle
                              _enterField.placeholderText = 'Succeeded'

                          } else {
                              _enterField.style = _errorTFStyle
                              _enterField.placeholderText = 'Error'
                          }
                          delay(1000 ,function() {
                              _enterField.style = _normalTFStyle
                              to_common()

                          })
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {},
                      onEscape : function() {
                          return_state()
                      }
                  }),
             pending :
                 ({
                      container :
                          ({
                               width: 75 * dp,
                               text: pending
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : {
                      },
                      onReturn : function() {
                      },
                      onListIndexChanged : function(index) {
                      },
                      onListIndexAccepted : function(index) {},
                      onEscape : function() {
                          return_state()
                      }
                  }),
             cmd :
                 ({
                      container :
                          ({
                               width: 60 * dp,
                               text: cmd
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : function (text) {
                          var rx = new RegExp("(" + commands.join('|') + ")\\s(.*)", 'i')
                          var rxmatch = text.match(rx)
                          if (rxmatch) {
                              var comm = rxmatch[1]
                              switch_state(comm)
                              _enterField.text = rxmatch[2]
                              if (modes[comm].hint !== undefined) {
                                  _enterField.placeholderText = modes[comm].hint
                              }
                          }
                      },
                      onReturn : function() {
                          this.onTextChanged(_enterField.text + ' ')
                      },
                      onListIndexChanged : function(index) {
                      },
                      onListIndexAccepted : function(index) {},
                      onEscape : function() {
                          return_state()
                      }
                  }),
             add :
                 ({
                      container :
                          ({
                               width: 60 * dp,
                               text: "add"
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      hint: 'new entry',
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : function (text) {
                          if (_resolver.contains(text)) {
                              _enterField.style = _redTFStyle
                          } else {
                              _enterField.style = _normalTFStyle
                          }
                      },
                      onReturn : function() {
                          if (_enterField.style === _normalTFStyle) {
                              switch_state(password, _enterField.text)
                              _enterField.placeholderText = 'for "' + _enterField.text + '"'
                              _enterField.text = ''
                          }
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {},
                      onPassword: function(o) {
                          if (o.name === undefined || o.password === undefined) {
                              return false
                          }
                          return _resolver.new_entry(o.name, o.password)
                      },
                      onEscape : function() {
                          return_state()
                          //FIXME Automaticly edjust
                          _enterField.style = _normalTFStyle
                      }
                  }),
             set :
                 ({
                      container :
                          ({
                               width: 52 * dp,
                               text: "set"
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : function (text) {
                          modes[common].onTextChanged(text)
                      },
                      onReturn : function() {
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {
                          if (listModel[index] === _enterField.text) {
                              switch_state(password,
                                           _enterField.text,
                                           this.hint)
                              _enterField.placeholderText = 'for "' + _enterField.text + '"'
                              _enterField.text = ''
                          } else {
                              _enterField.text = listModel[index]
                          }
                      },
                      onPassword: function(o) {
                          if (o.name === undefined || o.password === undefined) {
                              return false
                          }
                          return _resolver.set(o.name, o.password)
                      },
                      onEscape : function() {
                          return_state(actions_stack.pop().state)
                      }
                  }),
             del :
                 ({
                      container :
                          ({
                               width: 52 * dp,
                               text: "del"
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : function (text) {
                          modes[common].onTextChanged(text)
                      },
                      onReturn : function() {
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {
                          if (listModel[index] === _enterField.text) {
                              var oldtext = _enterField.placeholderText
                              if (this.onPassword({name: _enterField.text})) {
                                  _enterField.style = _successTFStyle
                                  _enterField.placeholderText = 'Succeeded'
                              } else {
                                  _enterField.style = _errorTFStyle
                                  _enterField.placeholderText = 'Error'
                              }
                              delay(1000 ,function() {
                                  _enterField.style = _normalTFStyle
                                  to_common()
                              })
                          } else {
                              _enterField.text = listModel[index]
                          }
                      },
                      onPassword: function(o) {
                          if (o.name === undefined) {
                              return false
                          }
                          return _resolver.del(o.name)
                      },
                      onEscape : function() {
                          return_state()
                      }
                  }),
             ren :
                 ({
                      container :
                          ({
                               width: 95 * dp,
                               text: "rename"
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : function (text) {
                          modes[common].onTextChanged(text)
                      },
                      onReturn : function() {},
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {
                          if (listModel[index] === _enterField.text) {
                              if (listModel[index] === _enterField.text) {
                                  switch_state(addinfo, _enterField.text)
                                  _enterField.placeholderText = 'for "' + _enterField.text + '"'
                                  _enterField.text = ''
                              } else {
                                  _enterField.text = listModel[index]
                              }
                          } else {
                              _enterField.text = listModel[index]
                          }
                      },
                      onRename: function(o) {
                          if (o.newname === undefined || o.oldname === undefined) {
                              return false
                          }
                          return _resolver.rename(o.oldname, o.newname)
                      },
                      onEscape : function() {
                          return_state()
                      }
                  }),
             esc :
                 ({
                      container :
                          ({
                               width: 60 * dp,
                               text: 'exit'
                           }),
                      passwordButton :
                          ({
                               visible : false
                           }),
                      tfstyle: _normalTFStyle,
                      echomode : TextInput.Normal,
                      placeholder : '',
                      onTextChanged : function (text) {
                      },
                      onReturn : function() {
                          Qt.quit()
                      },
                      onListIndexChanged : function(index) {},
                      onListIndexAccepted : function(index) {},
                      onEscape : function() {
                          return_state(actions_stack.pop().state)
                      }
                  }),
         })

    property string storedText: ''

    function rand_color() {
        var keys = Object.keys(colors)
        var randomint = Math.floor(Math.random() * keys.length)
        var randomval = colors[keys[randomint]]
        return randomval
    }

    function custom_hash_index(strval) {
        var hash = 0, i, chr, len;
        if (strval.length === 0) return hash;
        for (i = 0, len = strval.length; i < len; i++) {
            chr   = strval.charCodeAt(i);
            hash  = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }

        var keys = Object.keys(colors)
        var hashindex = Math.abs(hash) % (keys.length - 1)
        return colors[keys[hashindex]]
    }

    function _timer() {
        return Qt.createQmlObject("import QtQuick 2.0; Timer {}", mwn);
    }

    function delay(delayTime, cb) {
        _timer.interval = delayTime;
        _timer.repeat = false;
        _timer.triggered.connect(cb);
        _timer.start();
    }


    /*Behavior on height {
        NumberAnimation {
            duration: 150
            easing.type: Easing.InOutQuad
        }
    }*/

    Resolver {
        id: _resolver
        onKeysChanged: {
            if (modes[currentState].onKeysChanged !== undefined) {
                modes[currentState].onKeysChanged(newkeys)
            }
        }
    }

    property var listModel: modes[currentState].model

    x: (Screen.width - width) / 2
    y: (Screen.height - 480 * mwn.dp) / 2

    visible: true
    width: 640 * mwn.dp
    height: _textField.height

    title: qsTr("Hello World")
    flags: Qt.FramelessWindowHint | Qt.WA_TranslucentBackground | Qt.WindowStaysOnTopHint//| Qt.BypassWindowManagerHint

    Timer {
        id: _timer
    }

    Rectangle {
        id: _textField

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40 * mwn.dp
        color: "white"
        border.color: mwn.border_color
        border.width: mwn.border_width

        property alias customLeftSide: _customContainer.data

        property alias text: _enterField.text
        property var newEntry: function() {
            _customContainerContent.text = '<strong>NEW PASSWORD</strong>'
            mwn.storedText = _enterField.text
            mwn.currentState = mwn.password
            _enterField.text = ''
        }

        Rectangle {
            id: _customContainer

            //roperty int explicitwidth: currentState == mwn.password ? 130 * mwn.dp : 0
            property int explicitwidth: mwn.modes[currentState].container.width
            property alias text: _customContainerContent.text
            //width: children.width

            x: mwn.border_width
            y: mwn.border_width
            width: explicitwidth - 2*mwn.border_width
            height: parent.height - 2*mwn.border_width
            color: colors.green

            Behavior on width {
                NumberAnimation {duration: 150; easing.type: Easing.InOutQuad}
            }

            Rectangle {width: mwn.border_width; height: parent.height; color: mwn.border_color; anchors.right: parent.right}

            Text {
                id: _customContainerContent

                text: mwn.modes[currentState].container.text
                color: "white"
                font.pixelSize: 22 * mwn.dp
                font.bold: false
                anchors.fill: parent
                anchors.leftMargin: mwn.spacing
                renderType: Text.NativeRendering
                verticalAlignment: Qt.AlignVCenter
            }
        }

        TextField {
            id: _enterField

            x: _customContainer.width + mwn.border_width
            y: mwn.border_width
            width: parent.width - _customContainer.width - 2*mwn.border_width
            height: parent.height - 3*mwn.border_width
            font.pixelSize: 24 * mwn.dp
            echoMode: modes[currentState].echomode

            onTextChanged: {
                modes[currentState].onTextChanged(text)
            }

            focus: true
            placeholderText: modes[currentState].placeholder

            Keys.onPressed: {
                //console.log("Event key: " + event.key)
                switch (event.key) {
                case Qt.Key_Up:
                    _view.move(_view.up)
                    event.accepted = true
                    break
                case Qt.Key_Down:
                    _view.move(_view.down)
                    event.accepted = true
                    break
                }
            }
            Keys.onReturnPressed: {
                var storedState = currentState
                mwn.modes[storedState].onReturn()
                if (_view.count) {
                    mwn.modes[storedState].onListIndexAccepted(_view.currentIndex)
                }
                event.accepted = true
            }
            Keys.onEscapePressed: {
                modes[currentState].onEscape()
            }

            style:  modes[currentState].tfstyle

            Button {
                id: _passwordButton

                height: parent.height / 1.5
                width: height
                visible: modes[currentState].passwordButton.visible
                anchors.rightMargin: height / 2
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                style: ButtonStyle {
                    background: Image {
                        source: "eye.svg"
                    }
                }
            }
        }
    }

    Component {
        id: _normalTFStyle
        TextFieldStyle {
            background: Rectangle {
                border.color: mwn.border_color
                border.width: 0//mwn.border_width
            }
            renderType: Text.NativeRendering
            placeholderTextColor: colors.blue
        }
    }
    Component {
        id: _errorTFStyle
        TextFieldStyle {
            background: Rectangle {
                border.color: colors.red
                border.width: 0//mwn.border_width
            }
            renderType: Text.NativeRendering
            placeholderTextColor: colors.red
        }
    }
    Component {
        id: _successTFStyle
        TextFieldStyle {
            background: Rectangle {
                border.color: mwn.border_color
                border.width: 0//mwn.border_width
            }
            renderType: Text.NativeRendering
            placeholderTextColor: colors.green
        }
    }
    Component {
        id: _redTFStyle
        TextFieldStyle {
            background: Rectangle {
                border.color: mwn.border_color
                border.width: 0//mwn.border_width
            }
            renderType: Text.NativeRendering
            textColor: colors.red
        }
    }


    ListView {
        id: _view

        anchors.top: _textField.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: listModel.length * row_height
        clip: true
        model: listModel

        signal explicitIndexChanged(int index)

        readonly property int up : 0
        readonly property int down : 1

        function move(direction) {
            if (count < 2) return

            switch (direction) {
            case down:
                if (currentIndex === count - 1) {
                    currentIndex = currentIndex = 0
                } else {
                    currentIndex += 1
                }
                break
            case up:
                if (currentIndex === 0) {
                    currentIndex = count -1
                } else {
                    currentIndex -= 1
                }
                break
            }
            modes[currentState].onListIndexChanged(currentIndex)
        }

        delegate: Item {
            property string content: listModel[index]
            property string highlightColor: custom_hash_index(content)

            //color: "white"
            height: row_height
            width: parent.width
            Row {
                height: parent.height
                Rectangle {
                    id: __spacer
                    height: parent.height
                    color: 'transparent'
                    width: spacing
                }

                Rectangle {
                    //anchors.margins: spacing
                    anchors.verticalCenter: parent.verticalCenter
                    color: highlightColor
                    height: parent.height - spacing
                    width: height
                }

                Rectangle {
                    id: __spacer1
                    height: parent.height
                    color: 'transparent'
                    width: spacing
                }

                Text {
                    //anchors.margins: 4 * mwn.dp
                    anchors.verticalCenter: parent.verticalCenter
                    text: content
                    renderType: Text.NativeRendering
                    font.pixelSize: 14 * mwn.dp
                }
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    _view.currentIndex = index
                    modes[currentState].onListIndexAccepted(index)
                }
            }
        }
        //focus: true
        highlight: Rectangle {
            color: colors.grey100;
        }
        highlightMoveVelocity: 750
        onHeightChanged: {
            mwn.height = height + _textField.height
        }
    }

    Rectangle {
        id: __bottomframe

        width: parent.width
        height: mwn.border_width
        anchors.bottom: parent.bottom
        color: mwn.border_color
    }

    Rectangle {
        id: __leftframe

        width: mwn.border_width
        height: parent.height
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        color: mwn.border_color
    }

    Rectangle {
        id: __rightframe

        width: mwn.border_width
        height: parent.height
        anchors.right: parent.right
        color: mwn.border_color
    }

    style: ApplicationWindowStyle {
        background: Rectangle {
            color: "transparent"
        }
    }

}
