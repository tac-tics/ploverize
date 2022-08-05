//use x11rb::protocol::xtest::fake_input;
//use x11rb::xcb_ffi::XCBConnection;
//use x11rb::wrapper::ConnectionExt;
//use x11rb::protocol::xproto::{KEY_PRESS_EVENT, KEY_RELEASE_EVENT};
//
//
//pub fn do_thing() {
//    let (conn, _screen_num) = XCBConnection::connect(None).expect("COnnect failed");
//    let mut detail = 38; //0x024; // '$'
//    //let detail = 0x04d;
//    let root = 0;
//
//    loop {
//        fake_input(&conn, KEY_PRESS_EVENT, detail, 0, root, 0, 0, 0).expect("Fake input failed");
//        conn.sync().expect("Sync failed");
//        fake_input(&conn, KEY_RELEASE_EVENT, detail, 0, root, 0, 0, 0).expect("Fake input failed");
//        conn.sync().expect("Sync failed");
//        std::thread::sleep(std::time::Duration::from_secs(1));
//
//        detail += 1;
//        println!("{detail}");
//    }
//}
//

use autopilot::key::{KeyCode, Code};

pub fn send_keys(s: &str) {
    autopilot::key::type_string(s, &[], 0.0, 0.0);
    std::thread::sleep(std::time::Duration::from_millis(10));
}

pub fn send_backspaces(n: u8) {
    for _ in 0..n {
        autopilot::key::tap(&Code(KeyCode::Backspace), &[], 1, 1);
    }
    std::thread::sleep(std::time::Duration::from_millis(10));
}
