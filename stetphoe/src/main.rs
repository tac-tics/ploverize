#![allow(clippy::collapsible_if, clippy::new_without_default)]

use std::collections::HashMap;
use std::collections::VecDeque;
use std::fmt::Display;
use std::time::Duration;
use serialport::SerialPort;


fn main() {
    let ports = serialport::available_ports().expect("No ports found!");
    for p in &ports {
        println!("{}", p.port_name);
    }

    println!("{}", &ports[0].port_name);
    let port_filename = &ports[0].port_name; //"/dev/ttyACM0";

    let mut port = serialport::new(port_filename, 9600)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open port");

    let filename: &str = "../dictionaries/base.json";
    let dictionary = JsonDictionary::load_from_file(filename).unwrap();

    loop {
        let stroke = read_stroke(port.as_mut());
        let outline = stroke.clone().to_outline();
        let word = dictionary.lookup(outline.clone());
        println!("{} {:?}", stroke, word);
    }
}


const MAX_UNDO: usize = 1 << 15;

#[derive(Clone, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub struct Machine {
    undo_buffer: VecDeque<Stroke>,
    cap_next: bool,
    space_next: bool,
}

impl Machine {
    pub fn new() -> Self { 
        Self { 
            undo_buffer: VecDeque::new(), 
            cap_next: true,
            space_next: false, 
        }
    }

    pub fn apply(&mut self, stroke: Stroke) -> Vec<Command> {
        if self.undo_buffer.len() == MAX_UNDO {
            self.undo_buffer.pop_back();
        }
        self.undo_buffer.push_back(stroke);
        vec![]
    }
}

#[derive(Clone, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub struct Outline(Vec<Stroke>);

impl Outline {
    pub fn strokes(&self) -> &[Stroke] {
        let Outline(strokes) = self;
        strokes
    }
}

impl TryFrom<&str> for Outline {
    type Error = ();

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        todo!()
    }
}

impl std::ops::Div for Outline {
    type Output = Outline;

    fn div(self, rhs: Self) -> Self::Output {
        let Outline(self_strokes) = self;
        let Outline(rhs_strokes) = &rhs;
        let result_strokes: Vec<Stroke> = self_strokes.iter().chain(rhs_strokes.iter()).cloned().collect();
        Outline(result_strokes)
    }
}

impl From<Stroke> for Outline {
    fn from(stroke: Stroke) -> Self {
        Outline(vec![stroke])
    }
}

impl Display for Outline {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        for stroke in self.strokes() {
            write!(f, "{stroke}")?;
        }
        Ok(())
    }
}

pub trait Dictionary {
    fn lookup(&self, outline: Outline) -> Option<&str>;
}

pub struct JsonDictionary(HashMap<String, String>);

impl JsonDictionary {
    pub fn load_from_file<P: AsRef<std::path::Path>>(filepath: P) -> Result<Self, Box<dyn std::error::Error>> {
        let dictionary_json = std::fs::read_to_string(filepath)?;
        let dictionary: HashMap<String, String> = serde_json::from_str(&dictionary_json)?;
        Ok(JsonDictionary(dictionary))
    }
}

impl Dictionary for JsonDictionary {
    fn lookup(&self, outline: Outline) -> Option<&str> {
        let JsonDictionary(dictionary) = self;
        let entry = dictionary.get(&outline.to_string());
        entry.map(|s| s.as_str())
    }
}

pub enum Command {
    Output(String),
    Backspace(usize),
}

#[derive(Clone, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub struct Stroke(Vec<Key>);

impl Stroke {
    pub fn new(keys: &[Key]) -> Self {
        let mut key_vec: Vec<Key> = keys.to_vec();
        key_vec.sort();
        key_vec.dedup();
        Stroke(key_vec)
    }

    pub fn to_outline(self) -> Outline {
        Outline(vec![self])
    }
}

impl std::fmt::Display for Stroke {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let Stroke(keys) = self;
        let mut has_middle = false;

        for key in keys {
            let side = key_side(*key);
            if side == KeySide::Middle {
                has_middle = true;
            } else if side == KeySide::Right {
                if !has_middle {
                    write!(f, "-")?;
                    has_middle = true;
                }
            }

            write!(f, "{}", key_letter(*key))?;
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub enum Key {
    LeftS,
    LeftT,
    LeftK,
    LeftP,
    LeftW,
    LeftH,
    LeftR,

    MiddleA,
    MiddleO,
    MiddleStar,
    MiddleE,
    MiddleU,

    RightF,
    RightR,
    RightP,
    RightB,
    RightL,
    RightG,
    RightT,
    RightS,
    RightD,
    RightZ,

}

#[derive(Clone, Copy, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
enum KeySide {
    Left,
    Middle,
    Right,
}

fn key_side(key: Key) -> KeySide {
    for (target_key, side) in KEY_SIDES {
        if key == *target_key {
            return *side;
        }
    }
    unreachable!()
}

fn key_letter(key: Key) -> char {
    for (target_key, letter) in KEY_LETTER {
        if key == *target_key {
            return *letter;
        }
    }
    unreachable!()

}

const KEY_LETTER: &[(Key, char)] = &[
    (Key::LeftS, 'S'),
    (Key::LeftT, 'T'),
    (Key::LeftK, 'K'),
    (Key::LeftP, 'P'),
    (Key::LeftW, 'W'),
    (Key::LeftH, 'H'),
    (Key::LeftR, 'R'),

    (Key::MiddleA, 'A'),
    (Key::MiddleO, 'O'),
    (Key::MiddleStar, '*'),
    (Key::MiddleE, 'E'),
    (Key::MiddleU, 'U'),

    (Key::RightF, 'F'),
    (Key::RightR, 'R'),
    (Key::RightP, 'P'),
    (Key::RightB, 'B'),
    (Key::RightL, 'L'),
    (Key::RightG, 'G'),
    (Key::RightT, 'T'),
    (Key::RightS, 'S'),
    (Key::RightD, 'D'),
    (Key::RightZ, 'Z'),
];

const KEY_SIDES: &[(Key, KeySide)] = &[
    (Key::LeftS, KeySide::Left),
    (Key::LeftT, KeySide::Left),
    (Key::LeftK, KeySide::Left),
    (Key::LeftP, KeySide::Left),
    (Key::LeftW, KeySide::Left),
    (Key::LeftH, KeySide::Left),
    (Key::LeftR, KeySide::Left),

    (Key::MiddleA, KeySide::Middle),
    (Key::MiddleO, KeySide::Middle),
    (Key::MiddleStar, KeySide::Middle),
    (Key::MiddleE, KeySide::Middle),
    (Key::MiddleU, KeySide::Middle),

    (Key::RightF, KeySide::Right),
    (Key::RightR, KeySide::Right),
    (Key::RightP, KeySide::Right),
    (Key::RightB, KeySide::Right),
    (Key::RightL, KeySide::Right),
    (Key::RightG, KeySide::Right),
    (Key::RightT, KeySide::Right),
    (Key::RightS, KeySide::Right),
    (Key::RightD, KeySide::Right),
    (Key::RightZ, KeySide::Right),
];

const KEY_CODES: &[(Key, u64)] = &[
    (Key::LeftS, 0x000000002080),
    (Key::LeftT, 0x000000001080),
    (Key::LeftK, 0x000000000880),
    (Key::LeftP, 0x000000000480),
    (Key::LeftW, 0x000000000280),
    (Key::LeftH, 0x000000000180),
    (Key::LeftR, 0x000000400080),

    (Key::MiddleA, 0x000000200080),
    (Key::MiddleO, 0x000000100080),
    (Key::MiddleStar, 0x000000080080),
    (Key::MiddleStar, 0x000020000080),
    (Key::MiddleStar, 0x000000040080),
    (Key::MiddleStar, 0x000010000080),
    (Key::MiddleE, 0x000008000080),
    (Key::MiddleU, 0x000004000080),

    (Key::RightF, 0x000002000080),
    (Key::RightR, 0x000001000080),
    (Key::RightP, 0x004000000080),
    (Key::RightB, 0x002000000080),
    (Key::RightL, 0x001000000080),
    (Key::RightG, 0x000800000080),
    (Key::RightT, 0x000400000080),
    (Key::RightS, 0x000200000080),
    (Key::RightD, 0x000100000080),
    (Key::RightZ, 0x010000000080),
];

fn read_stroke(port: &mut dyn SerialPort) -> Stroke {
    let mut buf = [0; 6];
    let mut total_amount = 0;

    loop {
        let buf_slice = &mut buf[total_amount..6];
        match port.read(buf_slice) {
            Ok(amount) => {
                total_amount += amount;
            },
            Err(_e) => {
            }
        }

        if total_amount == 6 {
            break;
        }
    }

    let value: u64 =
        (buf[0] as u64) |
        (buf[1] as u64) << 8 |
        (buf[2] as u64) << 16 |
        (buf[3] as u64) << 24 |
        (buf[4] as u64) << 32 |
        (buf[5] as u64) << 40;

    let mut keys = vec![];
    for (key, key_value) in KEY_CODES {
        if value & key_value == *key_value {
            keys.push(*key);
        }
    }

    Stroke::new(keys.as_slice())
}
