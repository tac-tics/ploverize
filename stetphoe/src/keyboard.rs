use x11rb::xcb_ffi::XCBConnection;
use x11rb::wrapper::ConnectionExt;
use x11rb::protocol::xtest::fake_input;


pub fn do_thing() {
    let (conn, screen_num) = XCBConnection::connect(None).unwrap();
    let type_ = 2;
    let detail = 0x024; // '$'
    let root = 0;
    fake_input(&conn, type_, detail, 0, root, 0, 0, 0);

    conn.sync();
}
