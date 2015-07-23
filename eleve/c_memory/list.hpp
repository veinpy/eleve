#ifndef _LIST_HPP_
#define _LIST_HPP_

#include <map>
#include <iostream>
#include "node.hpp"

struct List;

struct __attribute__((packed)) TokenListPair
{
    ID token;
    std::unique_ptr<List> list;

    TokenListPair(ID t, std::unique_ptr<List> l): token(t), list(std::move(l)) {};
};

class ListIterator
{
    public:
    virtual void next() = 0;
    virtual Node* get() = 0;
};

class EmptyListIterator : public ListIterator
{
    public:
    void next() {};
    Node* get() { return nullptr; };
};

struct List
{
    // Recursive function used to add the occurence of a shingle
    virtual std::unique_ptr<List> add_shingle(shingle_const_iterator shingle_it, shingle_const_iterator shingle_end, int count=1) = 0;

    // To split the list in two, modifying it and returning a new one
    virtual TokenListPair split() = 0;
    // Get the size of the internal list, for calling split() if its too big
    virtual size_t size() const = 0;

    // Search for a sub-list
    virtual Node* search_child(shingle_const_iterator shingle_it, shingle_const_iterator shingle_end) = 0;

    // Iterator to the childs
    virtual std::unique_ptr<ListIterator> begin_childs() = 0;
};

#endif
