import QtQuick 2.7
import QtQuick.Controls 1.5
import QtQuick.Controls.Styles 1.4
import QtQuick.Window 2.0

import PyResolver 1.0

ApplicationWindow {
    id: mwn

    property real dpi: Screen.pixelDensity * 25.4
    property real dp: {return dpi < 120 ? 1 : dpi /160}
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
    readonly property string add: "add"
    readonly property string command: "command"

    property string currentState: state_machine.initial

    function switch_state(newstate) {
        actions_stack.push(state_machine[currentState])
        currentState = newstate
    }

    property var actions_stack : new Array()
    property var state_machine:
        ({
             initial : login,
             login :
                 ({
                      container :
                          ({
                               width: 0,
                               text: "",
                           }),
                      placeholder: "Password sir",
                      onTextChanged : function() {
                      },
                      onReturn : function() {
                          if (_resolver.check_password(_textField.text)) {
                              _enterField.style = _normalTFStyle
                              switch_state(common)
                          } else {
                              _textField.text = ''
                              _enterField.style = _errorTFStyle
                              var oldtext = _enterField.placeholderText
                              _enterField.placeholderText = "Incorrect, sir"
                              delay(1000 ,function() {
                                  _enterField.placeholderText = oldtext
                                  _enterField.style = _normalTFStyle
                              })
                          }
                      },
                      onEscape : function() {
                          Qt.quit()
                      }
                  }),
             common :
                 ({
                      container :
                          ({
                               width: 0,
                               text: ""
                           }),
                      onTextChanged : function () {},
                      onReturn : function() {},
                      onEscape : function() {}
                  }),
             password :
                 ({
                      container :
                          ({
                               width: 0,
                               text: ""
                           }),
                      onTextChanged : function () {},
                      onReturn : function() {},
                      onEscape : function() {}
                  }),
             add :
                 ({
                      container :
                          ({
                               width: 0,
                               text: ""
                           }),
                      onTextChanged : function () {},
                      onReturn : function() {},
                      onEscape : function() {}
                  })
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
    }

    property var pythonModel: currentState === login ?  [] : _resolver.keys
    property ListModel emptyModel: ListModel {}
    property ListModel fullModel:  ListModel {
        ListElement {name: "text1"}
        ListElement {name: "text2"}
        ListElement {name: "text3"}
        ListElement {name: "text4"}
    }

    property var alterModel: [
        'Key1',
        'Key2',
        'Key3'
    ]

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

        state: mwn.login
        states: [
            StateEx {
              id: _login
              name: mwn.login
              onReturn: {
                  console.log("Return")
              }
              onTextChanged: function (text) {
                  console.log("TextChanged")
              }
            },
            StateEx {
                name: mwn.common
            },
            State {
                name: mwn.add
                PropertyChanges {
                    target: _customContainer
                    explicitwidth: 50 * dp
                    text: "NEW"
                }
                when: mwn.currentState === mwn.add
            },
            State {
                name: mwn.password
                PropertyChanges {
                    target: _customContainer
                    explicitwidth: 140 * dp
                    text: "NEW PASSWORD"
                }
            }
        ]

        Rectangle {
            id: _customContainer

            //roperty int explicitwidth: currentState == mwn.password ? 130 * mwn.dp : 0
            property int explicitwidth: mwn.state_machine[currentState].container.width
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

                text: mwn.state_machine[currentState].container.text
                color: "white"
                font.pixelSize: 14 * mwn.dp
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
            echoMode: {
                login_succeeded ? TextInput.Normal : TextInput.Password
                switch (mwn.currentState) {
                case mwn.login:
                case mwn.password:
                    return TextInput.Password
                default:
                    return TextInput.Normal
                }
            }

            onTextChanged: {
                console.log("State: " + _textField.state)
                _login.onTextChanged(text)
                /*switch (currentState) {
                case mwn.login:
                    break
                case mwn.common:
                case mwn.add:
                    var keys = _resolver.keys
                    pythonModel = keys.filter(function(obj) {
                        var rx = new RegExp(text, 'i')
                        if (rx.test(obj)) {
                            return true
                        }
                        return false
                    })

                    mwn.pythonModel.length === 0 ? currentState = mwn.add : currentState = mwn.common
                    break
                }*/
            }

            focus: true
            placeholderText: state_machine[currentState].placeholder

            Keys.onPressed: {
                console.log("Event key: " + event.key)
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
                console.log("Return operations")

                var localMachine = mwn.state_machine
                localMachine[currentState].onReturn()
                mwn.state_machine = localMachine

                /*switch (mwn.currentState) {
                case mwn.password:
                    mwn.currentState = mwn.common
                    break;
                case mwn.common:
                    if (pythonModel.length === 0) {
                        _textField.newEntry()
                        currentState = add
                    } else {
                        _resolver.k2p_clipboard(pythonModel[_view.currentIndex])
                        mwn.hide()
                        Qt.quit()
                    }
                    break;
                }*/
                event.accepted = true
            }
            Keys.onEscapePressed: {
                console.log("Escape operations")
                switch (mwn.currentState) {
                case mwn.login:
                case mwn.common:
                    Qt.quit()
                    break
                case mwn.password:
                    _textField.text = mwn.storedText
                    mwn.currentState = mwn.common
                    break
                case mwn.add:
                    break
                }
            }

            style: _normalTFStyle
        }
    }

    Component {
        id: _normalTFStyle
        TextFieldStyle {
            background: Rectangle {
                border.color: mwn.border_color
                border.width: 0//mwn.border_width
            }
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
            placeholderTextColor: colors.red
        }
    }

    ListView {
        id: _view

        anchors.top: _textField.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: pythonModel.length * row_height
        clip: true
        model: pythonModel

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
        }

        delegate: Item {
            property string content: pythonModel[index]
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
