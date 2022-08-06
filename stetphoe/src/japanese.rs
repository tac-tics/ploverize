use lazy_static::lazy_static;
use std::collections::HashSet;
use super::Dictionary;
use super::Key;

pub struct KanaDictionary {}

impl KanaDictionary {
    pub fn new() -> Self {
        KanaDictionary {}
    }
}

impl Dictionary for KanaDictionary {
    fn lookup(&self, outline: crate::Outline) -> Option<&str> {
        println!("{:?}", outline);
        let mut keys: HashSet<Key> = outline.strokes()[0].keys().iter().cloned().collect();

        let mut result = String::new();

        for (combo, letter) in KEY_COMBOS.iter() {
            if combo.is_subset(&keys) {
                for remove_key in combo {
                    keys.remove(remove_key);
                }
                result.push(*letter);
            }
        }
        if result.is_empty() {
            None
        } else {
            result = convert_to_kana(&result);
            let result_box = Box::new(result);
            Some(Box::leak(result_box))
        }
    }
}

fn convert_to_kana(s: &str) -> String {
    let mut result = String::new();

    for (kana, romaji) in KANA.iter() {
        if s == *romaji {
            result.push(*kana);
            break;
        }
    }

    result
}

lazy_static! {
    static ref KEY_COMBOS: Vec<(HashSet<Key>, char)> = vec![ 
        ([Key::LeftT, Key::LeftP, Key::LeftH].into_iter().collect(), 'r'),
        ([Key::LeftT, Key::LeftH].into_iter().collect(), 'h'),
        ([Key::LeftT, Key::LeftP].into_iter().collect(), 'm'),
        ([Key::LeftP, Key::LeftH].into_iter().collect(), 'n'),
        ([Key::LeftT].into_iter().collect(), 't'),
        ([Key::LeftP].into_iter().collect(), 's'),
        ([Key::LeftH].into_iter().collect(), 'k'),

        ([Key::LeftK, Key::LeftW].into_iter().collect(), 'e'),
        ([Key::LeftR, Key::LeftW].into_iter().collect(), 'i'),
        ([Key::LeftK].into_iter().collect(), 'o'),
        ([Key::LeftW].into_iter().collect(), 'u'),
        ([Key::LeftR].into_iter().collect(), 'a'),
    ];
}


const KANA: &'static [(char, &'static str)] = &[
    ('あ', "a"),
    ('い', "i"),
    ('う', "u"),
    ('え', "e"),
    ('お', "o"),
    ('か', "ka"),
    ('き', "ki"),
    ('く', "ku"),
    ('け', "ke"),
    ('こ', "ko"),
    ('さ', "sa"),
    ('し', "si"),
    ('す', "su"),
    ('せ', "se"),
    ('そ', "so"),
    ('た', "ta"),
    ('ち', "ti"),
    ('つ', "tu"),
    ('て', "te"),
    ('と', "to"),
    ('な', "na"),
    ('に', "ni"),
    ('ぬ', "nu"),
    ('ね', "ne"),
    ('の', "no"),
    ('は', "ha"),
    ('ひ', "hi"),
    ('ふ', "hu"),
    ('へ', "he"),
    ('ほ', "ho"),
    ('ま', "ma"),
    ('み', "mi"),
    ('む', "mu"),
    ('め', "me"),
    ('も', "mo"),
    ('や', "ya"),
    ('ゆ', "yu"),
    ('よ', "yo"),
    ('ら', "ra"),
    ('り', "ri"),
    ('る', "ru"),
    ('れ', "re"),
    ('ろ', "ro"),
    ('わ', "wa"),
    ('を', "wo"),
    ('ん', "n"),
];
