/* ScummVM EOB1 繁體中文化 — Display-time substitution table impl */
#include "kyra/text/zh_substitute_eob.h"
#include <cstring>

namespace Kyra {

namespace {

struct Entry {
	const char *en;
	const char *zh;
};

// Sorted by approximate frequency / level coverage.
// Each ZH literal uses Big5 cp950 byte escapes for portability across
// build hosts (avoids file-encoding issues with the source tree).
static const Entry kEoB1ZhTable[] = {
	// Movement / navigation
	{ "going up...",          "\xa6\x56\xa4\x57\xa1\x44\xa1\x44\xa1\x44" },          // 向上．．．
	{ "going down...",        "\xa6\x56\xa4\x55\xa1\x44\xa1\x44\xa1\x44" },          // 向下．．．
	{ "you can't go that way.", "\xb5\x4c\xaa\x6b\xa8\xba\xbc\xcb\xa8\xab\xa1\x43" }, // 無法那樣走。
	{ "you can't go",         "\xb5\x4c\xaa\x6b\xa8\xab" },                          // 無法走

	// Lock / door messages
	{ "the lock has been picked!", "\xc2\xea\xa4\x77\xb3\xc2\xb6\x7d\xa1\x49" },     // 鎖已撬開！
	{ "appears jammed",       "\xa5\x69\xaf\xe0\xa8\xfb\xa6\xed" },                  // 可能卡住
	{ "appears jamm",         "\xa5\x69\xaf\xe0\xa8\xfb\xa6\xed" },                  // 可能卡住 (truncated form)
	{ "failed lock pick",     "\xb6\x7d\xc2\xea\xa5\xa2\xb1\xd1" },                  // 開鎖失敗
	{ "failed lock pi",       "\xb6\x7d\xc2\xea\xa5\xa2\xb1\xd1" },                  // 開鎖失敗 (truncated)
	{ "requires",             "\xbb\xdd\xad\x6e" },                                  // 需要
	{ "it doesn't fit.",      "\xa4\xa3\xa6\x58\xbe\x41\xa1\x43" },                  // 不合適。
	{ "the key fits",         "\xc6\x57\xb0\xcd\xa6\x58\xbe\x41" },                  // 鑰匙合適
	{ "dead end?",            "\xa6\xba\xb8\xf4\xa1\x48" },                          // 死路？

	// Trap / warning
	{ "do not disturb",       "\xbd\xd0\xa4\xc5\xa5\xb4\xc2\x5d" },                  // 請勿打擾
	{ "stow yer weapons.",    "\xbd\xd0\xa6\xac\xaa\x5a\xbe\xb9\xa1\x43" },          // 請收武器。
	{ "you were warned ",     "\xa7\x41\xa4\x77\xa9\x77\xb5\xb9\xc4\xb5\xa7\x69" },  // 你已被警告
	{ "get spiked!",          "\xa4\xa4\xa5\x40\xa8\xeb\xa1\x49" },                  // 中尖刺！

	// Specific level scenes
	{ "it smells terrible here.", "\xa6\xb9\xb3\x42\xa8\xfd\xa9\x52\xb7\xa5\xae\x74\xa1\x43" }, // 此處氣味極差。
	{ "skeleton",             "\xb0\xa9\xc5\xe9" },                                  // 骸體
	{ "star of navigation.",  "\xbe\xc9\xb1\x4b\xa4\xa7\xac\x50\xa1\x43" },          // 導引之星。

	// Sentinel (NULL marks end)
	{ nullptr, nullptr }
};

} // anonymous namespace

const char *zhSubstituteEoB(const char *en) {
	if (!en || !*en)
		return en;
	for (const Entry *e = kEoB1ZhTable; e->en != nullptr; ++e) {
		if (std::strcmp(en, e->en) == 0)
			return e->zh;
	}
	return en;
}

} // End of namespace Kyra
