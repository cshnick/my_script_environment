import QtQuick 2.7
import QtQuick.Controls 1.5
import QtQuick.Controls.Styles 1.4
import QtQuick.Window 2.0

import PyResolver 1.0

ApplicationWindow {
    id: mwn

    property real dpi: Screen.pixelDensity * 25.4
    property real dp: {return dpi < 120 ? 1 : dpi /160}

    Behavior on height {
        NumberAnimation {
            duration: 150
            easing.type: Easing.InOutQuad
        }
    }

    property ListModel fullModel:  ListModel {
        ListElement {name: "text1"}
        ListElement {name: "text2"}
        ListElement {name: "text3"}
        ListElement {name: "text4"}
    }
    property ListModel emptyModel: ListModel {}

    visible: true
    width: 640 * mwn.dp
    height: Math.min(480 * mwn.dp, __view.height)

    title: qsTr("Hello World")
    flags: Qt.FramelessWindowHint | Qt.WA_TranslucentBackground

    /*Rectangle {
        anchors.fill: parent
        color: "white"
    }*/

    TextField {
        id: __textField

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40 * mwn.dp
        font.pixelSize: 24 * mwn.dp
        onTextChanged: {
            __view.model = __view.model === emptyModel ? fullModel : emptyModel
        }
    }

    ListView {
        id: __view

        anchors.top: __textField.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: model.count * 40 * mwn.dp
        clip: true
        model: fullModel
        delegate: Rectangle {
            color: "white"
            height: 40 * mwn.dp
            width: parent.width
            Text {
                anchors.centerIn: parent
                text: name
            }
            Behavior on height {
                NumberAnimation {
                    duration: 150
                    easing.type: Easing.InOutQuad
                }
            }
        }
        onHeightChanged: {
            mwn.height = height + __textField.height
        }
    }

    style: ApplicationWindowStyle {
        background: Rectangle {
            color: "transparent"
        }
    }
}
